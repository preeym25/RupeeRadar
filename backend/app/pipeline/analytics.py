"""Financial metrics aggregation (Phase 1)."""

from app.models.analysis import FinancialMetrics
from app.models.transaction import RecurringGroup, Transaction


def compute_metrics(
    transactions: list[Transaction],
    recurring: list[RecurringGroup] | None = None,
) -> FinancialMetrics:
    raise NotImplementedError("Analytics engine will be implemented in Phase 1.")
