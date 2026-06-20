"""Pipeline orchestrator — wires ingestion through insight generation (Phase 2)."""

from __future__ import annotations

import logging
import time
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import UploadFile

from app.exceptions import InvalidFileTypeError, ParseError
from app.models.analysis import AnalysisResult, AnalysisSummary
from app.pipeline.analytics import compute_metrics
from app.pipeline.categorizer.rules import categorize
from app.pipeline.cleaner import clean
from app.pipeline.insights import generate_insights
from app.pipeline.ingestion.csv_parser import can_parse, parse_csv
from app.pipeline.recurrence import detect_recurring, merge_recurring_flags
from app.settings import get_settings

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {".csv"}


async def run_analysis(file: UploadFile) -> AnalysisResult:
    """Run the full analysis pipeline on an uploaded bank statement."""
    filename = file.filename or "upload.csv"
    ext = _extension(filename)

    if ext not in ALLOWED_EXTENSIONS:
        raise InvalidFileTypeError(
            f"Unsupported file type '{ext}'. Supported formats: CSV (.csv). "
            "Excel and PDF support coming in later phases."
        )

    if not can_parse(filename):
        raise InvalidFileTypeError(f"Cannot parse file: {filename}")

    job_id = str(uuid.uuid4())
    settings = get_settings()
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=settings.session_ttl_minutes)

    try:
        t0 = time.perf_counter()

        raw_transactions = await _parse_file(file, filename)
        logger.info(
            "Pipeline [%s]: parsed %d raw rows in %.2fs",
            job_id,
            len(raw_transactions),
            time.perf_counter() - t0,
        )

        t1 = time.perf_counter()
        clean_result = clean(raw_transactions)
        if not clean_result.transactions:
            raise ParseError(
                "No valid transactions found after cleaning. "
                "Check that dates and amounts are present in your export."
            )
        logger.info(
            "Pipeline [%s]: cleaned %d txns (dropped=%d, dupes=%d) in %.2fs",
            job_id,
            len(clean_result.transactions),
            clean_result.dropped_count,
            clean_result.duplicate_count,
            time.perf_counter() - t1,
        )

        t2 = time.perf_counter()
        categorized = categorize(clean_result.transactions)
        logger.info("Pipeline [%s]: categorized in %.2fs", job_id, time.perf_counter() - t2)

        t3 = time.perf_counter()
        recurring = detect_recurring(categorized)
        transactions = merge_recurring_flags(categorized, recurring)
        logger.info(
            "Pipeline [%s]: detected %d recurring groups in %.2fs",
            job_id,
            len(recurring),
            time.perf_counter() - t3,
        )

        t4 = time.perf_counter()
        metrics = compute_metrics(transactions, recurring)
        insights = generate_insights(transactions, metrics, recurring)
        logger.info(
            "Pipeline [%s]: metrics + %d insights in %.2fs",
            job_id,
            len(insights),
            time.perf_counter() - t4,
        )

        summary = AnalysisSummary(
            total_income=metrics.total_income,
            total_spend=metrics.total_spend,
            savings=metrics.savings,
            transaction_count=metrics.transaction_count,
            insight_count=len(insights),
        )

        return AnalysisResult(
            job_id=job_id,
            status="completed",
            filename=filename,
            created_at=now,
            expires_at=expires_at,
            transactions=transactions,
            recurring=recurring,
            metrics=metrics,
            insights=insights,
            summary=summary,
            error=None,
        )

    except (InvalidFileTypeError, ParseError):
        raise
    except ValueError as exc:
        raise ParseError(str(exc)) from exc
    except Exception as exc:
        logger.exception("Pipeline [%s]: unexpected error", job_id)
        raise ParseError(f"Failed to process statement: {exc}") from exc


async def _parse_file(file: UploadFile, filename: str) -> list:
    if filename.lower().endswith(".csv"):
        return await parse_csv(file)
    raise InvalidFileTypeError(f"No parser available for {filename}")


def _extension(filename: str) -> str:
    dot = filename.rfind(".")
    if dot == -1:
        return ""
    return filename[dot:].lower()
