"""Recurring payment detection (Phase 2)."""

from __future__ import annotations

import re
import statistics
import uuid
from collections import defaultdict
from datetime import date, timedelta

from app.models.transaction import (
    Category,
    RecurringFrequency,
    RecurringGroup,
    RecurringType,
    Transaction,
)

_EMI_KEYWORDS = re.compile(r"\b(emi|loan)\b", re.IGNORECASE)
_SIP_KEYWORDS = re.compile(r"\b(sip|mutual fund|mf)\b", re.IGNORECASE)
_INSURANCE_KEYWORDS = re.compile(r"\b(insurance|lic|policy)\b", re.IGNORECASE)
_RENT_KEYWORDS = re.compile(r"\b(rent|landlord|housing)\b", re.IGNORECASE)

_INTERVAL_RANGES: dict[RecurringFrequency, tuple[int, int]] = {
    RecurringFrequency.WEEKLY: (6, 9),
    RecurringFrequency.MONTHLY: (27, 35),
    RecurringFrequency.QUARTERLY: (85, 95),
    RecurringFrequency.YEARLY: (360, 370),
}


def detect_recurring(transactions: list[Transaction]) -> list[RecurringGroup]:
    """Identify repeating debit patterns (subscriptions, EMIs, rent, SIPs, etc.)."""
    debits = [
        t for t in transactions
        if t.type == "debit" and not t.is_duplicate
    ]

    groups: dict[str, list[Transaction]] = defaultdict(list)
    for txn in debits:
        groups[_group_key(txn)].append(txn)

    recurring_groups: list[RecurringGroup] = []

    for _key, txns in groups.items():
        if len(txns) < 2:
            continue

        txns = sorted(txns, key=lambda t: t.date)
        amounts = [t.amount for t in txns]
        mean_amt = statistics.mean(amounts)
        if mean_amt <= 0:
            continue

        if not _amounts_consistent(amounts, mean_amt):
            continue

        intervals = [
            (txns[i].date - txns[i - 1].date).days
            for i in range(1, len(txns))
        ]
        if not intervals:
            continue

        median_interval = statistics.median(intervals)
        frequency = _infer_frequency(median_interval)
        if frequency is None:
            continue

        representative = txns[0]
        category = representative.category or Category.OTHER
        rec_type = _infer_recurring_type(representative, category)
        group_id = str(uuid.uuid4())

        recurring_groups.append(
            RecurringGroup(
                id=group_id,
                label=_build_label(representative),
                category=category,
                type=rec_type,
                amount=round(mean_amt, 2),
                frequency=frequency,
                monthly_estimate=round(_to_monthly(mean_amt, frequency), 2),
                transaction_ids=[t.id for t in txns],
                next_expected_date=_next_expected_date(txns[-1].date, median_interval),
            )
        )

    return recurring_groups


def merge_recurring_flags(
    transactions: list[Transaction],
    recurring_groups: list[RecurringGroup],
) -> list[Transaction]:
    """Set is_recurring and recurring_group_id on transactions."""
    txn_to_group: dict[str, str] = {}
    for group in recurring_groups:
        for txn_id in group.transaction_ids:
            txn_to_group[txn_id] = group.id

    return [
        txn.model_copy(
            update={
                "is_recurring": txn.id in txn_to_group,
                "recurring_group_id": txn_to_group.get(txn.id),
            }
        )
        for txn in transactions
    ]


def _group_key(txn: Transaction) -> str:
    if txn.merchant:
        return f"merchant:{txn.merchant.upper()}"
    bucket = round(txn.amount / 100) * 100
    return f"amount:{bucket:.0f}"


def _amounts_consistent(amounts: list[float], mean_amt: float) -> bool:
    if len(amounts) == 1:
        return True
    stdev = statistics.stdev(amounts)
    if stdev / mean_amt <= 0.05:
        return True
    return all(abs(a - mean_amt) / mean_amt <= 0.05 for a in amounts)


def _infer_frequency(median_days: float) -> RecurringFrequency | None:
    for frequency, (low, high) in _INTERVAL_RANGES.items():
        if low <= median_days <= high:
            return frequency
    return None


def _to_monthly(amount: float, frequency: RecurringFrequency) -> float:
    if frequency == RecurringFrequency.WEEKLY:
        return amount * 4.33
    if frequency == RecurringFrequency.MONTHLY:
        return amount
    if frequency == RecurringFrequency.QUARTERLY:
        return amount / 3
    if frequency == RecurringFrequency.YEARLY:
        return amount / 12
    return amount


def _next_expected_date(last_date: date, median_interval: float) -> date:
    return last_date + timedelta(days=int(round(median_interval)))


def _build_label(txn: Transaction) -> str:
    if txn.merchant:
        return txn.merchant
    if txn.category == Category.RENT:
        return "Rent payment"
    if txn.category == Category.EMI:
        return "EMI payment"
    return f"₹{txn.amount:,.0f} recurring payment"


def _infer_recurring_type(txn: Transaction, category: Category) -> RecurringType:
    text = f"{txn.description_raw} {txn.description_clean}"
    if category == Category.RENT or _RENT_KEYWORDS.search(text):
        return RecurringType.RENT
    if category == Category.EMI or _EMI_KEYWORDS.search(text):
        return RecurringType.EMI
    if category == Category.INVESTMENTS or _SIP_KEYWORDS.search(text):
        return RecurringType.SIP
    if _INSURANCE_KEYWORDS.search(text):
        return RecurringType.INSURANCE
    if category == Category.SUBSCRIPTIONS:
        return RecurringType.SUBSCRIPTION
    return RecurringType.OTHER
