"""Recurring payment detection (Phase 2)."""

from app.models.transaction import RecurringGroup, Transaction


def detect_recurring(transactions: list[Transaction]) -> list[RecurringGroup]:
    raise NotImplementedError("Recurrence detector will be implemented in Phase 2.")
