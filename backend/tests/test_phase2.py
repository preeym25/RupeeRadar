"""Phase 2 tests — recurrence, insights, orchestrator, API integration."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.transaction import Category, RecurringType
from app.pipeline.insights import generate_insights
from app.pipeline.recurrence import detect_recurring, merge_recurring_flags
from app.pipeline.analytics import compute_metrics
from app.pipeline.categorizer.rules import categorize
from app.pipeline.cleaner import clean
from app.store.session_store import session_store

client = TestClient(app)
SAMPLE_CSV = Path(__file__).parent.parent.parent / "sample_data" / "sample_statement.csv"


# ---------------------------------------------------------------------------
# Recurrence detector
# ---------------------------------------------------------------------------

class TestRecurrence:
    def _monthly_debits(self, merchant: str, amount: float, months: list[int]) -> list:
        from tests.test_phase1 import make_transaction
        return [
            make_transaction(
                amount=amount,
                txn_type="debit",
                merchant=merchant,
                category=Category.SUBSCRIPTIONS,
                txn_date=date(2025, m, 5),
            )
            for m in months
        ]

    def test_detects_monthly_subscription(self):
        txns = self._monthly_debits("NETFLIX", 649.0, [1, 2, 3])
        categorized = categorize(txns)
        groups = detect_recurring(categorized)
        assert len(groups) >= 1
        netflix = next((g for g in groups if "NETFLIX" in g.label.upper()), None)
        assert netflix is not None
        assert netflix.type == RecurringType.SUBSCRIPTION
        assert netflix.frequency.value == "monthly"

    def test_single_occurrence_not_recurring(self):
        from tests.test_phase1 import make_transaction
        txns = categorize([
            make_transaction(
                amount=649.0,
                txn_type="debit",
                merchant="NETFLIX",
                category=Category.SUBSCRIPTIONS,
                txn_date=date(2025, 1, 5),
            )
        ])
        groups = detect_recurring(txns)
        assert len(groups) == 0

    def test_merge_recurring_flags(self):
        from tests.test_phase1 import make_transaction
        txns = categorize(self._monthly_debits("NETFLIX", 649.0, [1, 2, 3]))
        groups = detect_recurring(txns)
        merged = merge_recurring_flags(txns, groups)
        flagged = [t for t in merged if t.is_recurring]
        assert len(flagged) == 3
        assert all(t.recurring_group_id is not None for t in flagged)


# ---------------------------------------------------------------------------
# Insights generator
# ---------------------------------------------------------------------------

class TestInsights:
    def test_at_least_three_insights(self):
        from tests.test_phase1 import make_transaction
        txns = categorize([
            make_transaction(300.0, "debit", category=Category.FOOD),
            make_transaction(15000.0, "debit", category=Category.EMI),
            make_transaction(85000.0, "credit", category=Category.SALARY),
        ])
        metrics = compute_metrics(txns)
        insights = generate_insights(txns, metrics, [])
        assert len(insights) >= 3
        assert all(i.source == "template" for i in insights)


# ---------------------------------------------------------------------------
# API integration
# ---------------------------------------------------------------------------

class TestAnalyzeAPI:
    def setup_method(self):
        session_store._jobs.clear()

    def test_analyze_sample_csv(self):
        if not SAMPLE_CSV.exists():
            pytest.skip("sample_statement.csv not found")

        with open(SAMPLE_CSV, "rb") as f:
            response = client.post(
                "/api/v1/analyze",
                files={"file": ("sample_statement.csv", f, "text/csv")},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["job_id"]
        assert len(data["transactions"]) > 0
        assert data["metrics"] is not None
        assert data["metrics"]["total_spend"] > 0
        assert len(data["insights"]) >= 3
        assert data["summary"]["insight_count"] >= 3

    def test_get_analysis_by_job_id(self):
        if not SAMPLE_CSV.exists():
            pytest.skip("sample_statement.csv not found")

        with open(SAMPLE_CSV, "rb") as f:
            post = client.post(
                "/api/v1/analyze",
                files={"file": ("sample_statement.csv", f, "text/csv")},
            )
        job_id = post.json()["job_id"]

        get = client.get(f"/api/v1/analyze/{job_id}")
        assert get.status_code == 200
        assert get.json()["job_id"] == job_id

    def test_get_transactions_paginated(self):
        if not SAMPLE_CSV.exists():
            pytest.skip("sample_statement.csv not found")

        with open(SAMPLE_CSV, "rb") as f:
            post = client.post(
                "/api/v1/analyze",
                files={"file": ("sample_statement.csv", f, "text/csv")},
            )
        job_id = post.json()["job_id"]

        resp = client.get(f"/api/v1/analyze/{job_id}/transactions?page=1&size=10")
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] > 0
        assert len(body["transactions"]) <= 10

    def test_delete_analysis(self):
        if not SAMPLE_CSV.exists():
            pytest.skip("sample_statement.csv not found")

        with open(SAMPLE_CSV, "rb") as f:
            post = client.post(
                "/api/v1/analyze",
                files={"file": ("sample_statement.csv", f, "text/csv")},
            )
        job_id = post.json()["job_id"]

        delete = client.delete(f"/api/v1/analyze/{job_id}")
        assert delete.status_code == 204

        get = client.get(f"/api/v1/analyze/{job_id}")
        assert get.status_code == 404

    def test_invalid_file_type(self):
        response = client.post(
            "/api/v1/analyze",
            files={"file": ("bad.docx", b"not a csv", "application/octet-stream")},
        )
        assert response.status_code == 400

    def test_empty_csv_rejected(self):
        response = client.post(
            "/api/v1/analyze",
            files={"file": ("empty.csv", b"", "text/csv")},
        )
        assert response.status_code == 422

    def test_get_unknown_job_returns_404(self):
        response = client.get("/api/v1/analyze/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404


class TestGenerateSampleOutput:
    """Generate sample_analysis_output.json for deliverable."""

    def test_write_sample_output(self):
        if not SAMPLE_CSV.exists():
            pytest.skip("sample_statement.csv not found")

        session_store._jobs.clear()
        with open(SAMPLE_CSV, "rb") as f:
            response = client.post(
                "/api/v1/analyze",
                files={"file": ("sample_statement.csv", f, "text/csv")},
            )
        assert response.status_code == 200
        output_path = Path(__file__).parent.parent.parent / "sample_data" / "sample_analysis_output.json"
        with open(output_path, "w", encoding="utf-8") as out:
            json.dump(response.json(), out, indent=2, default=str)
