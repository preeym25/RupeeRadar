from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, Query, UploadFile

from app.exceptions import InvalidFileTypeError, ParseError, PipelineError
from app.models.analysis import AnalysisResult
from app.models.transaction import Category
from app.pipeline.orchestrator import run_analysis
from app.store.session_store import session_store

router = APIRouter(prefix="/analyze", tags=["analyze"])


def _handle_pipeline_error(exc: PipelineError) -> HTTPException:
    return HTTPException(status_code=exc.status_code, detail=str(exc))


@router.post("", response_model=AnalysisResult)
async def analyze_statement(file: UploadFile = File(...)) -> AnalysisResult:
    """Upload a bank statement CSV and run the full analysis pipeline."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="File is required.")

    try:
        result = await run_analysis(file)
    except InvalidFileTypeError as exc:
        raise _handle_pipeline_error(exc)
    except ParseError as exc:
        raise _handle_pipeline_error(exc)
    except PipelineError as exc:
        raise _handle_pipeline_error(exc)

    return session_store.save(result)


@router.get("/{job_id}", response_model=AnalysisResult)
async def get_analysis(job_id: str) -> AnalysisResult:
    """Retrieve a stored analysis result by job ID."""
    result = session_store.get(job_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Analysis not found or session expired.")
    return result


@router.get("/{job_id}/transactions")
async def get_transactions(
    job_id: str,
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=500),
    category: str | None = Query(None),
    recurring: bool | None = Query(None),
) -> dict:
    """Paginated transaction list with optional filters."""
    result = session_store.get(job_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Analysis not found or session expired.")

    txns = result.transactions

    if category:
        try:
            cat_enum = Category(category)
            txns = [t for t in txns if t.category == cat_enum]
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid category. Valid values: {[c.value for c in Category]}",
            )

    if recurring is not None:
        txns = [t for t in txns if t.is_recurring == recurring]

    total = len(txns)
    start = (page - 1) * size
    end = start + size
    page_items = txns[start:end]

    return {
        "job_id": job_id,
        "total": total,
        "page": page,
        "size": size,
        "pages": max(1, (total + size - 1) // size),
        "transactions": page_items,
    }


from fastapi.responses import HTMLResponse
from app.report.generator import generate_html_report

@router.get("/{job_id}/report", response_class=HTMLResponse)
async def get_report(job_id: str, format: str = Query("html")):
    """Generate a printable HTML report."""
    result = session_store.get(job_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Analysis not found or session expired.")
    
    html_content = generate_html_report(result)
    return HTMLResponse(content=html_content)




@router.delete("/{job_id}", status_code=204)
async def delete_analysis(job_id: str) -> None:
    """Purge session data for privacy."""
    if not session_store.delete(job_id):
        raise HTTPException(status_code=404, detail="Analysis not found or already deleted.")
