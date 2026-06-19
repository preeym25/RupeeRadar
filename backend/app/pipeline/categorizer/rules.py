"""Rule-based transaction categorizer (Phase 1)."""

from app.models.transaction import Transaction


def categorize(transactions: list[Transaction]) -> list[Transaction]:
    raise NotImplementedError("Rule categorizer will be implemented in Phase 1.")
