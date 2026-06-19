"""Groq LLM fallback categorizer for low-confidence transactions (Phase 5)."""

from app.models.transaction import Transaction


def categorize_with_llm(transactions: list[Transaction]) -> list[Transaction]:
    raise NotImplementedError("Groq LLM categorizer will be implemented in Phase 5.")
