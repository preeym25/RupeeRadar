"""CSV bank statement parser (Phase 1)."""

from __future__ import annotations

import io
import re
from typing import Any

import pandas as pd
from fastapi import UploadFile

from app.models.transaction import RawTransaction

# ---------------------------------------------------------------------------
# Header keyword mapping for fuzzy column detection
# ---------------------------------------------------------------------------
_DATE_KEYWORDS = ["date", "txn date", "transaction date", "value date", "posting date"]
_DESC_KEYWORDS = ["narration", "description", "particulars", "details", "remarks", "transaction details"]
_DEBIT_KEYWORDS = ["withdrawal", "debit", "dr", "dr amount", "withdrawal amt", "debit amt", "debit amount"]
_CREDIT_KEYWORDS = ["deposit", "credit", "cr", "cr amount", "deposit amt", "credit amt", "credit amount"]
_BALANCE_KEYWORDS = ["balance", "closing balance", "available balance"]
_REF_KEYWORDS = ["reference", "ref no", "cheque no", "chq no", "transaction id"]

# Date formats to try in order (Indian banks first)
_DATE_FORMATS = [
    "%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d",
    "%d/%m/%y", "%d-%m-%y",
    "%d %b %Y", "%d %B %Y",
    "%Y/%m/%d",
]

# Rows that are metadata / summary lines, not transactions
_SKIP_ROW_PATTERNS = re.compile(
    r"^(opening balance|closing balance|total|sub.?total|summary|brought forward|carried forward|page|statement of|account (no|number))",
    re.IGNORECASE,
)


def can_parse(filename: str) -> bool:
    return filename.lower().endswith(".csv")


def _fuzzy_match_col(col: str, keywords: list[str]) -> int:
    """Return a relevance score (higher = better match) for a column name."""
    col_lower = col.lower().strip()
    for i, kw in enumerate(keywords):
        if kw in col_lower:
            return len(keywords) - i  # earlier keyword = higher priority
    # Partial word match
    for i, kw in enumerate(keywords):
        for word in kw.split():
            if word in col_lower:
                return max(1, len(keywords) - i - 1)
    return 0


def _detect_columns(df: pd.DataFrame) -> dict[str, str | None]:
    """Fuzzy-match DataFrame columns to semantic roles."""
    mapping: dict[str, str | None] = {
        "date": None,
        "description": None,
        "debit": None,
        "credit": None,
        "balance": None,
        "reference": None,
    }
    role_keywords = {
        "date": _DATE_KEYWORDS,
        "description": _DESC_KEYWORDS,
        "debit": _DEBIT_KEYWORDS,
        "credit": _CREDIT_KEYWORDS,
        "balance": _BALANCE_KEYWORDS,
        "reference": _REF_KEYWORDS,
    }
    for role, keywords in role_keywords.items():
        best_score = 0
        best_col: str | None = None
        for col in df.columns:
            score = _fuzzy_match_col(str(col), keywords)
            if score > best_score:
                best_score = score
                best_col = col
        if best_score > 0:
            mapping[role] = best_col
    return mapping


def _parse_amount(val: Any) -> float | None:
    """Parse INR amount strings like '₹1,234.56', 'Rs. 1234', '1,234' into float."""
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return None
    s = str(val).strip()
    # Strip currency symbols: ₹, 'Rs', 'Cr', 'Dr' (but NOT the decimal point)
    s = re.sub(r"₹", "", s)
    s = re.sub(r"\bRs\.?\s*", "", s, flags=re.IGNORECASE)
    s = re.sub(r"\b(Cr|Dr)\.?\s*", "", s, flags=re.IGNORECASE)
    # Remove commas used as thousands separator
    s = s.replace(",", "").strip()
    if not s or s in ("-", "+"):
        return None
    try:
        return abs(float(s))  # Always return absolute; sign resolved by column role
    except ValueError:
        return None


def _parse_date(val: Any) -> str | None:
    """Try multiple date formats; return None if unparseable."""
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return None
    s = str(val).strip()
    if not s:
        return None
    # Try pandas automatic parsing first
    for fmt in _DATE_FORMATS:
        try:
            return pd.to_datetime(s, format=fmt).strftime("%Y-%m-%d")
        except Exception:
            pass
    # Fallback: let pandas infer
    try:
        return pd.to_datetime(s, dayfirst=True).strftime("%Y-%m-%d")
    except Exception:
        return None


def _find_header_row(raw_lines: list[str]) -> int:
    """Find the index of the actual header row by looking for keyword columns."""
    keywords = set(
        _DATE_KEYWORDS + _DESC_KEYWORDS + _DEBIT_KEYWORDS + _CREDIT_KEYWORDS
    )
    for i, line in enumerate(raw_lines[:20]):  # Search within first 20 rows
        lower = line.lower()
        matches = sum(1 for kw in keywords if kw in lower)
        if matches >= 2:
            return i
    return 0  # Default to first row


async def parse_csv(file: UploadFile) -> list[RawTransaction]:
    """Parse a CSV bank statement into RawTransaction objects."""
    content = await file.read()
    if not content or not content.strip():
        raise ValueError("Empty file — no transactions found.")

    # Handle BOM
    if content.startswith(b"\xef\xbb\xbf"):
        content = content[3:]

    # Decode with fallback encodings
    text: str
    for encoding in ("utf-8", "latin-1", "windows-1252", "cp1252"):
        try:
            text = content.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        text = content.decode("utf-8", errors="replace")

    lines = text.splitlines()
    if not lines:
        raise ValueError("Empty file — no transactions found.")

    # Find actual header row (skip bank logo / metadata rows)
    header_idx = _find_header_row(lines)
    csv_text = "\n".join(lines[header_idx:])

    try:
        df = pd.read_csv(io.StringIO(csv_text), dtype=str)
    except Exception as exc:
        raise ValueError(f"Failed to parse CSV: {exc}") from exc

    # Drop fully-empty rows
    df = df.dropna(how="all")
    df.columns = [str(c).strip() for c in df.columns]

    if df.empty:
        raise ValueError("No transactions found after parsing.")

    # Detect columns
    col_map = _detect_columns(df)

    if not col_map["date"] and not col_map["description"]:
        raise ValueError(
            "Unrecognized CSV layout — could not find date or description columns. "
            "Try exporting a CSV directly from your net banking portal."
        )

    raw_transactions: list[RawTransaction] = []

    for row_idx, row in df.iterrows():
        # Skip summary / balance rows
        desc_col = col_map["description"]
        raw_desc = str(row[desc_col]).strip() if desc_col and not _is_nan(row.get(desc_col)) else ""
        if _SKIP_ROW_PATTERNS.match(raw_desc):
            continue

        date_str = _parse_date(row.get(col_map["date"])) if col_map["date"] else None
        debit = _parse_amount(row.get(col_map["debit"])) if col_map["debit"] else None
        credit = _parse_amount(row.get(col_map["credit"])) if col_map["credit"] else None
        balance = _parse_amount(row.get(col_map["balance"])) if col_map["balance"] else None
        reference = str(row.get(col_map["reference"], "")).strip() if col_map["reference"] else None
        if reference == "nan":
            reference = None

        if not raw_desc:
            raw_desc = "Unknown transaction"

        raw_transactions.append(
            RawTransaction(
                date=date_str,
                description=raw_desc,
                debit=debit if debit and debit > 0 else None,
                credit=credit if credit and credit > 0 else None,
                balance=balance,
                reference=reference or None,
                source_row=int(row_idx) + header_idx + 1,  # 1-based, offset by skipped rows
            )
        )

    if not raw_transactions:
        raise ValueError("No transactions found in CSV.")

    return raw_transactions


def _is_nan(val: Any) -> bool:
    if val is None:
        return True
    if isinstance(val, float) and pd.isna(val):
        return True
    return str(val).strip().lower() in ("nan", "none", "")

