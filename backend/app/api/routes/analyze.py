from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/analyze", tags=["analyze"])


@router.post("")
async def analyze_statement() -> dict:
    """Upload and analyze a bank statement. Implemented in Phase 2."""
    raise HTTPException(
        status_code=501,
        detail="Analysis pipeline not yet implemented. Complete Phase 1–2.",
    )
