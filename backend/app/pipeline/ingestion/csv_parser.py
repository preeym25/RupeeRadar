"""CSV bank statement parser (Phase 1)."""

from fastapi import UploadFile

from app.models.transaction import RawTransaction


def can_parse(filename: str) -> bool:
    return filename.lower().endswith(".csv")


async def parse_csv(file: UploadFile) -> list[RawTransaction]:
    raise NotImplementedError("CSV parser will be implemented in Phase 1.")
