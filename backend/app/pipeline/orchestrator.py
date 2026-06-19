"""Pipeline orchestrator — wires ingestion through insight generation (Phase 2)."""

from fastapi import UploadFile

from app.models.analysis import AnalysisResult


async def run_analysis(file: UploadFile) -> AnalysisResult:
    raise NotImplementedError("Pipeline orchestrator will be implemented in Phase 2.")
