"""Template and LLM-powered spending insights (Phase 2 / Phase 5)."""

from __future__ import annotations

import uuid
from collections import defaultdict

from app.models.analysis import FinancialMetrics, Insight, MonthlySpend
from app.models.transaction import Category, RecurringGroup, RecurringType, Transaction


def generate_insights(
    transactions: list[Transaction],
    metrics: FinancialMetrics,
    recurring: list[RecurringGroup],
) -> list[Insight]:
    """Produce personalized insights from metrics; always returns at least 3."""
    insights: list[Insight] = []
    seen_titles: set[str] = set()

    def add(
        title: str,
        body: str,
        amount: float | None = None,
        category: str | None = None,
        severity: str = "info",
    ) -> None:
        if title in seen_titles:
            return
        seen_titles.add(title)
        insights.append(
            Insight(
                id=str(uuid.uuid4()),
                title=title,
                body=body,
                category=category,
                amount=round(amount, 2) if amount is not None else None,
                severity=severity,
                source="template",
            )
        )

    # Top category share
    if metrics.top_categories:
        top = metrics.top_categories[0]
        add(
            title="Top spending category",
            body=(
                f"{top.category.value} is your largest expense at "
                f"₹{top.amount:,.0f} ({top.percentage:.1f}% of total spend)."
            ),
            amount=top.amount,
            category=top.category.value,
        )

    # Recurring total
    if recurring and metrics.recurring_monthly_total > 0:
        add(
            title="Fixed recurring payments",
            body=(
                f"Fixed recurring payments total ₹{metrics.recurring_monthly_total:,.0f}/month "
                f"across {len(recurring)} merchants."
            ),
            amount=metrics.recurring_monthly_total,
            severity="warning",
        )

    # Biggest debit
    if metrics.biggest_debit:
        bd = metrics.biggest_debit
        add(
            title="Largest transaction",
            body=(
                f"Your largest transaction was ₹{bd.amount:,.0f} "
                f"({bd.description}) on {bd.date.isoformat()}."
            ),
            amount=bd.amount,
            category=bd.category.value if bd.category else None,
        )

    # Subscription count
    subscriptions = [g for g in recurring if g.type == RecurringType.SUBSCRIPTION]
    if subscriptions:
        sub_total = sum(g.monthly_estimate for g in subscriptions)
        add(
            title="Active subscriptions",
            body=(
                f"You have {len(subscriptions)} active subscriptions costing "
                f"₹{sub_total:,.0f}/month."
            ),
            amount=sub_total,
            category=Category.SUBSCRIPTIONS.value,
        )

    # MoM category spike (if ≥ 2 months)
    mom_insight = _mom_spike_insight(metrics.monthly_spend, transactions)
    if mom_insight:
        add(**mom_insight)

    # Savings insight
    if metrics.savings_rate is not None:
        if metrics.savings >= 0:
            add(
                title="Savings this period",
                body=(
                    f"You saved ₹{metrics.savings:,.0f} "
                    f"({metrics.savings_rate * 100:.1f}% of income)."
                ),
                amount=metrics.savings,
                severity="positive",
            )
        else:
            add(
                title="Spending exceeded income",
                body=(
                    f"You spent ₹{abs(metrics.savings):,.0f} more than you earned "
                    f"during this period."
                ),
                amount=abs(metrics.savings),
                severity="warning",
            )

    # Fallback insights to guarantee ≥ 3
    if len(insights) < 3:
        add(
            title="Total spend",
            body=(
                f"You spent ₹{metrics.total_spend:,.0f} across "
                f"{metrics.transaction_count} transactions between "
                f"{metrics.period_start.isoformat()} and {metrics.period_end.isoformat()}."
            ),
            amount=metrics.total_spend,
        )

    if len(insights) < 3 and metrics.total_income > 0:
        add(
            title="Total income",
            body=f"Total income credited during this period was ₹{metrics.total_income:,.0f}.",
            amount=metrics.total_income,
            severity="positive",
        )

    if len(insights) < 3:
        add(
            title="Analysis summary",
            body=(
                f"RupeeRadar analyzed {metrics.transaction_count} transactions "
                f"over {len(metrics.monthly_spend)} month(s) of activity."
            ),
            amount=float(metrics.transaction_count),
        )

    return insights[:8]


def _mom_spike_insight(
    monthly_spend: list[MonthlySpend],
    transactions: list[Transaction],
) -> dict | None:
    if len(monthly_spend) < 2:
        return None

    sorted_months = sorted(monthly_spend, key=lambda m: m.month)
    prev_month, curr_month = sorted_months[-2], sorted_months[-1]

    if prev_month.amount <= 0:
        return None

    change_pct = (curr_month.amount - prev_month.amount) / prev_month.amount * 100
    if abs(change_pct) < 15:
        return None

    # Find category with biggest MoM increase
    prev_cats = _category_spend_by_month(transactions, prev_month.month)
    curr_cats = _category_spend_by_month(transactions, curr_month.month)

    best_cat: str | None = None
    best_delta = 0.0
    for cat, curr_amt in curr_cats.items():
        prev_amt = prev_cats.get(cat, 0.0)
        if prev_amt > 0:
            delta_pct = (curr_amt - prev_amt) / prev_amt * 100
            if delta_pct > best_delta:
                best_delta = delta_pct
                best_cat = cat

    if best_cat and best_delta >= 15:
        curr_amt = curr_cats.get(best_cat, 0.0)
        return {
            "title": f"{best_cat} spending spike",
            "body": (
                f"{best_cat} spending increased {best_delta:.0f}% compared to last month "
                f"(₹{curr_amt:,.0f} in {curr_month.month})."
            ),
            "amount": curr_amt,
            "category": best_cat,
            "severity": "warning",
        }

    # Overall spend MoM
    direction = "increased" if change_pct > 0 else "decreased"
    return {
        "title": "Month-over-month spend change",
        "body": (
            f"Total spending {direction} {abs(change_pct):.0f}% from "
            f"{prev_month.month} to {curr_month.month}."
        ),
        "amount": curr_month.amount,
        "severity": "warning" if change_pct > 0 else "positive",
    }


def _category_spend_by_month(
    transactions: list[Transaction],
    month: str,
) -> dict[str, float]:
    totals: dict[str, float] = defaultdict(float)
    for txn in transactions:
        if txn.type != "debit" or txn.is_duplicate:
            continue
        if txn.date.strftime("%Y-%m") != month:
            continue
        cat = txn.category.value if txn.category else Category.OTHER.value
        totals[cat] += txn.amount
    return dict(totals)
