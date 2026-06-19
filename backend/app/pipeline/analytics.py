"""Financial metrics aggregation (Phase 1)."""

from __future__ import annotations

from collections import defaultdict

from app.models.analysis import CategorySummary, FinancialMetrics, MonthlySpend, TransactionSummary
from app.models.transaction import Category, RecurringGroup, Transaction


def compute_metrics(
    transactions: list[Transaction],
    recurring: list[RecurringGroup] | None = None,
) -> FinancialMetrics:
    """
    Compute aggregate financial metrics from a list of categorized transactions.
    """
    if not transactions:
        raise ValueError("Cannot compute metrics: no transactions provided.")

    # Exclude duplicate transactions from totals
    active = [t for t in transactions if not t.is_duplicate]

    # Period range
    dates = [t.date for t in active]
    period_start = min(dates)
    period_end = max(dates)

    # Income / spend totals
    credits = [t for t in active if t.type == "credit"]
    debits = [t for t in active if t.type == "debit"]

    total_income = round(sum(t.amount for t in credits), 2)
    total_spend = round(sum(t.amount for t in debits), 2)
    savings = round(total_income - total_spend, 2)
    savings_rate: float | None = None
    if total_income > 0:
        savings_rate = round(savings / total_income, 4)

    transaction_count = len(active)

    # Category breakdown (debits only)
    by_category_raw: dict[str, float] = defaultdict(float)
    cat_txn_count: dict[str, int] = defaultdict(int)
    for t in debits:
        cat_key = t.category.value if t.category else Category.OTHER.value
        by_category_raw[cat_key] = round(by_category_raw[cat_key] + t.amount, 2)
        cat_txn_count[cat_key] += 1

    # Ensure all categories appear (even at 0) so UI can display them
    by_category: dict[str, float] = {cat.value: 0.0 for cat in Category}
    by_category.update(by_category_raw)

    # Top categories (sorted by spend desc, non-zero only)
    top_categories: list[CategorySummary] = sorted(
        [
            CategorySummary(
                category=Category(cat),
                amount=round(amount, 2),
                percentage=round(amount / total_spend * 100, 2) if total_spend > 0 else 0.0,
                transaction_count=cat_txn_count.get(cat, 0),
            )
            for cat, amount in by_category.items()
            if amount > 0
        ],
        key=lambda x: x.amount,
        reverse=True,
    )

    # Biggest debit and credit
    biggest_debit: TransactionSummary | None = None
    biggest_credit: TransactionSummary | None = None

    if debits:
        bd = max(debits, key=lambda t: t.amount)
        biggest_debit = TransactionSummary(
            id=bd.id,
            date=bd.date,
            description=bd.description_clean,
            amount=bd.amount,
            category=bd.category,
        )

    if credits:
        bc = max(credits, key=lambda t: t.amount)
        biggest_credit = TransactionSummary(
            id=bc.id,
            date=bc.date,
            description=bc.description_clean,
            amount=bc.amount,
            category=bc.category,
        )

    # Monthly spend (debits grouped by YYYY-MM)
    monthly_raw: dict[str, float] = defaultdict(float)
    monthly_count: dict[str, int] = defaultdict(int)
    for t in debits:
        month_key = t.date.strftime("%Y-%m")
        monthly_raw[month_key] = round(monthly_raw[month_key] + t.amount, 2)
        monthly_count[month_key] += 1

    monthly_spend: list[MonthlySpend] = sorted(
        [
            MonthlySpend(
                month=month,
                amount=round(amount, 2),
                transaction_count=monthly_count[month],
            )
            for month, amount in monthly_raw.items()
        ],
        key=lambda x: x.month,
    )

    # Recurring monthly total from detected groups
    recurring_monthly_total = 0.0
    if recurring:
        recurring_monthly_total = round(
            sum(g.monthly_estimate for g in recurring), 2
        )

    return FinancialMetrics(
        period_start=period_start,
        period_end=period_end,
        total_income=total_income,
        total_spend=total_spend,
        savings=savings,
        savings_rate=savings_rate,
        transaction_count=transaction_count,
        by_category=by_category,
        top_categories=top_categories,
        biggest_debit=biggest_debit,
        biggest_credit=biggest_credit,
        monthly_spend=monthly_spend,
        recurring_monthly_total=recurring_monthly_total,
    )

