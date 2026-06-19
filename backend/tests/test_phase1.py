"""Phase 1 unit tests — CSV parser, cleaner, categorizer, analytics."""

from __future__ import annotations

import io
from datetime import date
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.transaction import Category, RawTransaction, Transaction
from app.pipeline.analytics import compute_metrics
from app.pipeline.categorizer.rules import categorize
from app.pipeline.cleaner import CleanResult, clean


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_raw(
    date_str: str = "01/01/2025",
    description: str = "Test transaction",
    debit: float | None = 100.0,
    credit: float | None = None,
    source_row: int = 1,
) -> RawTransaction:
    return RawTransaction(
        date=date_str,
        description=description,
        debit=debit,
        credit=credit,
        balance=None,
        reference=None,
        source_row=source_row,
    )


def make_transaction(
    amount: float = 100.0,
    txn_type: str = "debit",
    description_clean: str = "Test",
    description_raw: str = "Test",
    merchant: str | None = None,
    category: Category | None = None,
    category_confidence: float = 0.0,
    txn_date: date = date(2025, 1, 1),
    is_duplicate: bool = False,
) -> Transaction:
    import uuid
    return Transaction(
        id=str(uuid.uuid4()),
        date=txn_date,
        description_raw=description_raw,
        description_clean=description_clean,
        amount=amount,
        type=txn_type,
        merchant=merchant,
        category=category,
        category_confidence=category_confidence,
        is_duplicate=is_duplicate,
    )


# ===========================================================================
# 1. CSV Parser tests
# ===========================================================================

class TestCSVParser:
    """Tests for app.pipeline.ingestion.csv_parser"""

    @pytest.mark.asyncio
    async def test_parse_standard_hdfc_style(self):
        """Standard Indian bank CSV with Narration/Withdrawal/Deposit columns."""
        from app.pipeline.ingestion.csv_parser import parse_csv

        csv_content = (
            "Transaction Date,Narration,Withdrawal Amt.,Deposit Amt.,Balance\n"
            "01/01/2025,NEFT CR-SALARY,,85000.00,170000.00\n"
            "02/01/2025,UPI/SWIGGY@ybl,292.00,,169708.00\n"
        )
        mock_file = AsyncMock()
        mock_file.read = AsyncMock(return_value=csv_content.encode("utf-8"))
        mock_file.filename = "test.csv"

        result = await parse_csv(mock_file)
        assert len(result) == 2
        assert result[0].credit == 85000.0
        assert result[0].debit is None
        assert result[1].debit == 292.0
        assert result[1].credit is None

    @pytest.mark.asyncio
    async def test_parse_empty_file_raises(self):
        from app.pipeline.ingestion.csv_parser import parse_csv

        mock_file = AsyncMock()
        mock_file.read = AsyncMock(return_value=b"")
        mock_file.filename = "empty.csv"

        with pytest.raises(ValueError, match="[Ee]mpty"):
            await parse_csv(mock_file)

    @pytest.mark.asyncio
    async def test_parse_bom_stripped(self):
        """UTF-8 BOM should be stripped and parsed correctly."""
        from app.pipeline.ingestion.csv_parser import parse_csv

        csv_content = (
            "Transaction Date,Narration,Withdrawal Amt.,Deposit Amt.,Balance\n"
            "05/01/2025,NETFLIX,649.00,,100000.00\n"
        )
        bom_content = b"\xef\xbb\xbf" + csv_content.encode("utf-8")
        mock_file = AsyncMock()
        mock_file.read = AsyncMock(return_value=bom_content)

        result = await parse_csv(mock_file)
        assert len(result) == 1
        assert result[0].debit == 649.0

    @pytest.mark.asyncio
    async def test_parse_date_formats(self):
        """Parser should handle dd/mm/yyyy, dd-mm-yyyy, yyyy-mm-dd."""
        from app.pipeline.ingestion.csv_parser import parse_csv

        csv_content = (
            "Date,Description,Debit,Credit\n"
            "01-02-2025,Swiggy,200.00,\n"
            "2025-03-15,Netflix,649.00,\n"
        )
        mock_file = AsyncMock()
        mock_file.read = AsyncMock(return_value=csv_content.encode("utf-8"))

        result = await parse_csv(mock_file)
        assert len(result) == 2
        assert result[0].date == "2025-02-01"
        assert result[1].date == "2025-03-15"

    @pytest.mark.asyncio
    async def test_skip_balance_summary_rows(self):
        """Opening/Closing balance rows should be skipped."""
        from app.pipeline.ingestion.csv_parser import parse_csv

        csv_content = (
            "Date,Narration,Debit,Credit,Balance\n"
            "01/01/2025,Opening Balance,,,50000.00\n"
            "02/01/2025,Swiggy,300.00,,49700.00\n"
            "31/01/2025,Closing Balance,,,49700.00\n"
        )
        mock_file = AsyncMock()
        mock_file.read = AsyncMock(return_value=csv_content.encode("utf-8"))

        result = await parse_csv(mock_file)
        # Opening and Closing Balance rows should be excluded
        descriptions = [r.description for r in result]
        assert not any("Balance" in d for d in descriptions)
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_amount_with_currency_symbols(self):
        """Amounts like '₹1,234.56' or 'Rs.1234' should parse correctly."""
        from app.pipeline.ingestion.csv_parser import parse_csv

        csv_content = (
            "Date,Narration,Debit,Credit\n"
            "01/01/2025,Amazon,₹1234.00,\n"
            "02/01/2025,Salary,,Rs.85000\n"
        )
        mock_file = AsyncMock()
        mock_file.read = AsyncMock(return_value=csv_content.encode("utf-8"))

        result = await parse_csv(mock_file)
        assert result[0].debit == 1234.0
        assert result[1].credit == 85000.0

    def test_can_parse_csv(self):
        from app.pipeline.ingestion.csv_parser import can_parse
        assert can_parse("statement.csv") is True
        assert can_parse("statement.CSV") is True
        assert can_parse("statement.xlsx") is False
        assert can_parse("statement.pdf") is False


# ===========================================================================
# 2. Cleaner tests
# ===========================================================================

class TestCleaner:
    def test_basic_clean(self):
        raws = [make_raw("01/01/2025", "SWIGGY ORDER", 300.0)]
        result = clean(raws)
        assert len(result.transactions) == 1
        assert result.dropped_count == 0
        txn = result.transactions[0]
        assert txn.amount == 300.0
        assert txn.type == "debit"
        assert txn.date == date(2025, 1, 1)

    def test_upi_description_cleaned(self):
        """UPI boilerplate stripped, merchant extracted."""
        raws = [make_raw(
            "02/01/2025",
            "UPI/SWIGGY@ybl-HDFC0001234-123456789012-Payment",
            409.0,
        )]
        result = clean(raws)
        txn = result.transactions[0]
        assert "SWIGGY" in txn.description_clean.upper() or txn.merchant == "SWIGGY"
        # Long numeric refs removed from clean desc
        assert "123456789012" not in txn.description_clean

    def test_deduplication(self):
        """Same (date, amount, normalized_description) → second marked duplicate."""
        raws = [
            make_raw("01/01/2025", "NETFLIX SUBSCRIPTION", 649.0, source_row=1),
            make_raw("01/01/2025", "NETFLIX SUBSCRIPTION", 649.0, source_row=2),
        ]
        result = clean(raws)
        assert result.duplicate_count == 1
        duplicates = [t for t in result.transactions if t.is_duplicate]
        assert len(duplicates) == 1

    def test_zero_amount_dropped(self):
        raws = [make_raw("01/01/2025", "Test", debit=0.0, credit=0.0)]
        result = clean(raws)
        assert result.dropped_count == 1
        assert len(result.transactions) == 0

    def test_invalid_date_dropped(self):
        raws = [make_raw("INVALID_DATE", "Test", 100.0)]
        result = clean(raws)
        assert result.dropped_count == 1
        assert len(result.transactions) == 0

    def test_credit_transaction(self):
        raws = [make_raw("01/01/2025", "NEFT CR-SALARY", debit=None, credit=85000.0)]
        result = clean(raws)
        txn = result.transactions[0]
        assert txn.type == "credit"
        assert txn.amount == 85000.0

    def test_merchant_extraction_swiggy(self):
        raws = [make_raw("01/01/2025", "UPI/SWIGGY@ybl-HDFC0001234-999888777666-Payment", 300.0)]
        result = clean(raws)
        assert result.transactions[0].merchant == "SWIGGY"

    def test_merchant_extraction_netflix(self):
        raws = [make_raw("05/01/2025", "AUTOPAY NETFLIX COM MUMBAI", 649.0)]
        result = clean(raws)
        assert result.transactions[0].merchant == "NETFLIX"

    def test_phone_number_stripped(self):
        raws = [make_raw("01/01/2025", "UPI/9876543210@paytm Transfer", 2000.0)]
        result = clean(raws)
        assert "9876543210" not in result.transactions[0].description_clean

    def test_empty_description_replaced(self):
        raws = [RawTransaction(date="01/01/2025", description="", debit=100.0, source_row=1)]
        result = clean(raws)
        assert result.transactions[0].description_clean == "Unknown transaction"

    def test_date_formats_supported(self):
        """Multiple date formats should all parse correctly."""
        raws = [
            make_raw("01/01/2025", "A", 100.0, source_row=1),
            make_raw("01-01-2025", "B", 200.0, source_row=2),
            make_raw("2025-01-01", "C", 300.0, source_row=3),
        ]
        result = clean(raws)
        assert result.dropped_count == 0
        assert all(t.date == date(2025, 1, 1) for t in result.transactions)


# ===========================================================================
# 3. Categorizer tests
# ===========================================================================

class TestCategorizer:
    def _make_txns(self, items: list[tuple]) -> list[Transaction]:
        """items: list of (desc_raw, desc_clean, merchant, txn_type)"""
        txns = []
        for raw, clean_d, merchant, txn_type in items:
            txns.append(make_transaction(
                description_raw=raw,
                description_clean=clean_d,
                merchant=merchant,
                txn_type=txn_type,
            ))
        return txns

    def test_swiggy_to_food(self):
        txns = self._make_txns([("SWIGGY", "SWIGGY", "SWIGGY", "debit")])
        result = categorize(txns)
        assert result[0].category == Category.FOOD

    def test_zomato_to_food(self):
        txns = self._make_txns([("ZOMATO ORDER", "ZOMATO ORDER", "ZOMATO", "debit")])
        result = categorize(txns)
        assert result[0].category == Category.FOOD

    def test_uber_to_travel(self):
        txns = self._make_txns([("UBER INDIA RIDE MUMBAI", "UBER INDIA RIDE MUMBAI", "UBER", "debit")])
        result = categorize(txns)
        assert result[0].category == Category.TRAVEL

    def test_amazon_to_shopping(self):
        txns = self._make_txns([("AMAZON PAY INDIA", "AMAZON PAY INDIA", "AMAZON PAY", "debit")])
        result = categorize(txns)
        assert result[0].category == Category.SHOPPING

    def test_netflix_to_subscriptions(self):
        txns = self._make_txns([("AUTOPAY NETFLIX COM", "AUTOPAY NETFLIX COM", "NETFLIX", "debit")])
        result = categorize(txns)
        assert result[0].category == Category.SUBSCRIPTIONS

    def test_groww_sip_to_investments(self):
        txns = self._make_txns([("SIP GROWW MUTUAL FUND", "SIP GROWW MUTUAL FUND", "GROWW", "debit")])
        result = categorize(txns)
        assert result[0].category == Category.INVESTMENTS

    def test_salary_credit(self):
        txns = self._make_txns([("NEFT CR-ACME TECH-SALARY", "ACME TECH SALARY", None, "credit")])
        result = categorize(txns)
        assert result[0].category == Category.SALARY

    def test_emi_category(self):
        txns = self._make_txns([("EMI HDFC LOAN A/C XX1234", "EMI HDFC LOAN", None, "debit")])
        result = categorize(txns)
        assert result[0].category == Category.EMI

    def test_unknown_merchant_is_other(self):
        txns = self._make_txns([("UPI/UNKNOWN SHOP 123", "UNKNOWN SHOP", None, "debit")])
        result = categorize(txns)
        assert result[0].category == Category.OTHER
        assert result[0].category_confidence == 0.0

    def test_rent_category(self):
        txns = self._make_txns([("RENT PAYMENT LANDLORD", "RENT PAYMENT LANDLORD", None, "debit")])
        result = categorize(txns)
        assert result[0].category == Category.RENT

    def test_airtel_bills(self):
        txns = self._make_txns([("AIRTEL POSTPAID AUTOPAY", "AIRTEL POSTPAID AUTOPAY", "AIRTEL", "debit")])
        result = categorize(txns)
        assert result[0].category == Category.BILLS

    def test_uber_eats_vs_uber_trip(self):
        """UBER EATS should be Food, UBER should be Travel."""
        txns = [
            make_transaction(description_raw="UBER EATS ORDER", description_clean="UBER EATS ORDER",
                             merchant="UBER EATS", txn_type="debit"),
            make_transaction(description_raw="UBER INDIA RIDE", description_clean="UBER INDIA RIDE",
                             merchant="UBER", txn_type="debit"),
        ]
        result = categorize(txns)
        assert result[0].category == Category.FOOD
        assert result[1].category == Category.TRAVEL

    def test_confidence_assigned(self):
        txns = [make_transaction(description_raw="NETFLIX SUB", description_clean="NETFLIX SUB",
                                 merchant="NETFLIX", txn_type="debit")]
        result = categorize(txns)
        assert result[0].category_confidence > 0.5


# ===========================================================================
# 4. Analytics tests
# ===========================================================================

class TestAnalytics:
    def _make_debits(self, amounts_and_cats: list[tuple]) -> list[Transaction]:
        """List of (amount, category, date_override=None)"""
        txns = []
        for item in amounts_and_cats:
            amount, cat = item[0], item[1]
            d = item[2] if len(item) > 2 else date(2025, 1, 15)
            txns.append(make_transaction(amount=amount, txn_type="debit",
                                         category=cat, txn_date=d))
        return txns

    def test_basic_metrics(self):
        txns = [
            make_transaction(amount=85000.0, txn_type="credit",
                             category=Category.SALARY, txn_date=date(2025, 1, 1)),
            make_transaction(amount=300.0, txn_type="debit",
                             category=Category.FOOD, txn_date=date(2025, 1, 2)),
        ]
        metrics = compute_metrics(txns)
        assert metrics.total_income == 85000.0
        assert metrics.total_spend == 300.0
        assert metrics.savings == 84700.0
        assert metrics.savings_rate == pytest.approx(84700 / 85000, rel=1e-4)

    def test_period_range(self):
        txns = [
            make_transaction(amount=100.0, txn_type="debit", txn_date=date(2025, 1, 5)),
            make_transaction(amount=200.0, txn_type="debit", txn_date=date(2025, 3, 20)),
        ]
        metrics = compute_metrics(txns)
        assert metrics.period_start == date(2025, 1, 5)
        assert metrics.period_end == date(2025, 3, 20)

    def test_no_credits_savings_rate_none(self):
        txns = [make_transaction(amount=500.0, txn_type="debit",
                                 category=Category.FOOD, txn_date=date(2025, 1, 1))]
        metrics = compute_metrics(txns)
        assert metrics.total_income == 0.0
        assert metrics.savings == -500.0
        assert metrics.savings_rate is None  # Edge case A-05

    def test_by_category_totals(self):
        txns = [
            make_transaction(300.0, "debit", category=Category.FOOD),
            make_transaction(200.0, "debit", category=Category.FOOD),
            make_transaction(15000.0, "debit", category=Category.EMI),
        ]
        metrics = compute_metrics(txns)
        assert metrics.by_category[Category.FOOD.value] == 500.0
        assert metrics.by_category[Category.EMI.value] == 15000.0

    def test_top_categories_sorted(self):
        txns = [
            make_transaction(300.0, "debit", category=Category.FOOD),
            make_transaction(15000.0, "debit", category=Category.EMI),
            make_transaction(649.0, "debit", category=Category.SUBSCRIPTIONS),
        ]
        metrics = compute_metrics(txns)
        amounts = [c.amount for c in metrics.top_categories]
        assert amounts == sorted(amounts, reverse=True)

    def test_monthly_spend_buckets(self):
        txns = [
            make_transaction(300.0, "debit", txn_date=date(2025, 1, 10)),
            make_transaction(400.0, "debit", txn_date=date(2025, 1, 20)),
            make_transaction(500.0, "debit", txn_date=date(2025, 2, 5)),
        ]
        metrics = compute_metrics(txns)
        months = {m.month: m.amount for m in metrics.monthly_spend}
        assert months["2025-01"] == 700.0
        assert months["2025-02"] == 500.0

    def test_biggest_debit_and_credit(self):
        txns = [
            make_transaction(100.0, "debit"),
            make_transaction(45000.0, "debit"),
            make_transaction(85000.0, "credit"),
        ]
        metrics = compute_metrics(txns)
        assert metrics.biggest_debit is not None
        assert metrics.biggest_debit.amount == 45000.0
        assert metrics.biggest_credit is not None
        assert metrics.biggest_credit.amount == 85000.0

    def test_duplicate_excluded_from_totals(self):
        txns = [
            make_transaction(500.0, "debit"),
            make_transaction(500.0, "debit", is_duplicate=True),
        ]
        metrics = compute_metrics(txns)
        assert metrics.total_spend == 500.0  # Duplicate excluded

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            compute_metrics([])

    def test_category_percentages(self):
        txns = [
            make_transaction(300.0, "debit", category=Category.FOOD),
            make_transaction(700.0, "debit", category=Category.RENT),
        ]
        metrics = compute_metrics(txns)
        food_summary = next(c for c in metrics.top_categories if c.category == Category.FOOD)
        rent_summary = next(c for c in metrics.top_categories if c.category == Category.RENT)
        assert food_summary.percentage == pytest.approx(30.0, rel=1e-2)
        assert rent_summary.percentage == pytest.approx(70.0, rel=1e-2)


# ===========================================================================
# 5. End-to-end mini pipeline test (sample_statement.csv)
# ===========================================================================

class TestEndToEndPipeline:
    @pytest.mark.asyncio
    async def test_sample_csv_full_pipeline(self):
        """Run the full Phase 1 pipeline on sample_statement.csv."""
        from pathlib import Path

        from app.pipeline.ingestion.csv_parser import parse_csv

        sample_path = Path(__file__).parent.parent.parent / "sample_data" / "sample_statement.csv"
        if not sample_path.exists():
            pytest.skip("sample_statement.csv not found")

        content = sample_path.read_bytes()
        mock_file = AsyncMock()
        mock_file.read = AsyncMock(return_value=content)

        # 1. Parse
        raw_txns = await parse_csv(mock_file)
        assert len(raw_txns) > 0

        # 2. Clean
        clean_result = clean(raw_txns)
        assert len(clean_result.transactions) > 0

        # 3. Categorize
        categorized = categorize(clean_result.transactions)
        non_other = [t for t in categorized if t.category != Category.OTHER]
        # At least 60% should be categorized (not Other)
        assert len(non_other) / len(categorized) >= 0.6

        # 4. Analytics
        metrics = compute_metrics(categorized)
        assert metrics.total_income > 0
        assert metrics.total_spend > 0
        assert metrics.transaction_count > 0
        assert len(metrics.top_categories) > 0
        assert len(metrics.monthly_spend) >= 1
