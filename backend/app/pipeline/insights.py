"""Template and LLM-powered spending insights (Phase 2 / Phase 5)."""

from app.models.analysis import FinancialMetrics, Insight
from app.models.transaction import RecurringGroup, Transaction


def generate_insights(
    transactions: list[Transaction],
    metrics: FinancialMetrics,
    recurring: list[RecurringGroup],
) -> list[Insight]:
    raise NotImplementedError("Insight generator will be implemented in Phase 2.")
