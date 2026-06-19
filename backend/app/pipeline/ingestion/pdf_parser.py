"""PDF bank statement parser (Phase 6)."""

from fastapi import UploadFile

from app.models.transaction import RawTransaction


def can_parse(filename: str) -> bool:
    return filename.lower().endswith(".pdf")


async def parse_pdf(file: UploadFile) -> list[RawTransaction]:
    raise NotImplementedError("PDF parser will be implemented in Phase 6.")
