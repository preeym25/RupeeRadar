from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import analyze, health
from app.exceptions import PipelineError
from app.settings import get_settings
from app.store.session_store import session_store

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    purged = session_store.purge_expired()
    if purged:
        print(f"Purged {purged} expired analysis session(s) on startup.")
    yield
    session_store.purge_expired()


app = FastAPI(
    title="RupeeRadar API",
    description="AI-powered personal finance assistant for bank statement analysis",
    version="0.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(PipelineError)
async def pipeline_error_handler(_request: Request, exc: PipelineError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": str(exc)})


app.include_router(health.router, prefix="/api/v1")
app.include_router(analyze.router, prefix="/api/v1")
