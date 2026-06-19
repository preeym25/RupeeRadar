"""Groq LLM client for categorization and insight enrichment (Phase 5)."""

from groq import Groq

from app.settings import get_settings


def get_groq_client() -> Groq | None:
    settings = get_settings()
    if not settings.enable_llm or not settings.groq_api_key:
        return None
    return Groq(api_key=settings.groq_api_key)


def is_llm_available() -> bool:
    return get_groq_client() is not None
