from fastapi import APIRouter

from app.models.analysis import HealthResponse
from app.settings import get_settings

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="ok",
        service="rupeeradar-api",
        llm_provider="groq",
        llm_enabled=settings.enable_llm and bool(settings.groq_api_key),
    )
