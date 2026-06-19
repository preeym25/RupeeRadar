"""Transaction cleaner — normalize raw rows into canonical transactions (Phase 1)."""

from app.models.transaction import RawTransaction, Transaction


def clean(raw_transactions: list[RawTransaction]) -> list[Transaction]:
    raise NotImplementedError("Cleaner will be implemented in Phase 1.")
