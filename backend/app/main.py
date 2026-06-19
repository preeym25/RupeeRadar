from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import analyze, health
from app.settings import get_settings

settings = get_settings()

app = FastAPI(
    title="RupeeRadar API",
    description="AI-powered personal finance assistant for bank statement analysis",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1")
app.include_router(analyze.router, prefix="/api/v1")
