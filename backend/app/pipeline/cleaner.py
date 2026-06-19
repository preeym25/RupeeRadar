"""Transaction cleaner — normalize raw rows into canonical Transaction records (Phase 1)."""

from __future__ import annotations

import hashlib
import re
import uuid
from dataclasses import dataclass
from datetime import date as date_type
from typing import Any

from app.models.transaction import RawTransaction, Transaction

# ---------------------------------------------------------------------------
# Regex patterns for UPI / IMPS / NEFT boilerplate stripping
# ---------------------------------------------------------------------------
_UPI_BOILERPLATE = re.compile(
    r"(UPI/|/UPI|IMPS/|/P2A/|/IMPS|NEFT-|NEFT/|RTGS-|RTGS/|AUTOPAY\s+)\s*",
    re.IGNORECASE,
)
_UPI_REF_NUMBERS = re.compile(r"\b\d{10,}\b")  # Long numeric references (also PII guard)
_UPI_HANDLE = re.compile(r"@[a-zA-Z0-9]+\b")   # e.g. @paytm, @ybl
_BANK_BRANCH_CODES = re.compile(r"\b[A-Z]{4}\d{7}\b")  # HDFC0001234 style codes
_CARD_MASK = re.compile(r"\b\d{4,6}[Xx*]+\d{2,4}\b")   # POS card masks
_POS_PREFIX = re.compile(r"^POS\s+", re.IGNORECASE)
_CHANNEL_PREFIXES = re.compile(
    r"^(NEFT CR[-\s]|NEFT[-\s]INW[-\s]|IMPS/P2A/|SI\s+|AUTOPAY\s+)",
    re.IGNORECASE,
)
_EXTRA_WHITESPACE = re.compile(r"\s{2,}")
_PHONE_NUMBERS = re.compile(r"\b[6-9]\d{9}\b")  # Indian mobile numbers
_TRAILING_SEPARATORS = re.compile(r"[-/\s]+$")

# Merchant hint keywords mapping (pattern → extracted merchant name)
_MERCHANT_HINTS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"swiggy", re.IGNORECASE), "SWIGGY"),
    (re.compile(r"zomato", re.IGNORECASE), "ZOMATO"),
    (re.compile(r"eatfit", re.IGNORECASE), "EATFIT"),
    (re.compile(r"dominos|domino's", re.IGNORECASE), "DOMINOS"),
    (re.compile(r"mcdonalds|mcdonald's|mcd\b", re.IGNORECASE), "MCDONALDS"),
    (re.compile(r"burger king", re.IGNORECASE), "BURGER KING"),
    (re.compile(r"netflix", re.IGNORECASE), "NETFLIX"),
    (re.compile(r"spotify", re.IGNORECASE), "SPOTIFY"),
    (re.compile(r"youtube", re.IGNORECASE), "YOUTUBE"),
    (re.compile(r"hotstar|disney\+?", re.IGNORECASE), "HOTSTAR"),
    (re.compile(r"prime video|amazon prime", re.IGNORECASE), "AMAZON PRIME"),
    (re.compile(r"amazon\s*pay|amzn\s*pay", re.IGNORECASE), "AMAZON PAY"),
    (re.compile(r"amzn\s*mktp|amazon\s*mktp", re.IGNORECASE), "AMAZON"),
    (re.compile(r"\bamazon\b(?!\s*(pay|prime))", re.IGNORECASE), "AMAZON"),
    (re.compile(r"\bamzn\b", re.IGNORECASE), "AMAZON"),
    (re.compile(r"flipkart", re.IGNORECASE), "FLIPKART"),
    (re.compile(r"myntra", re.IGNORECASE), "MYNTRA"),
    (re.compile(r"\bajio\b", re.IGNORECASE), "AJIO"),
    (re.compile(r"meesho", re.IGNORECASE), "MEESHO"),
    (re.compile(r"uber\s*eats", re.IGNORECASE), "UBER EATS"),
    (re.compile(r"\buber\b", re.IGNORECASE), "UBER"),
    (re.compile(r"\bola\b", re.IGNORECASE), "OLA"),
    (re.compile(r"rapido", re.IGNORECASE), "RAPIDO"),
    (re.compile(r"irctc", re.IGNORECASE), "IRCTC"),
    (re.compile(r"makemytrip|mmt", re.IGNORECASE), "MAKEMYTRIP"),
    (re.compile(r"goibibo", re.IGNORECASE), "GOIBIBO"),
    (re.compile(r"fastag|netc\s*toll|npci\s*netc", re.IGNORECASE), "FASTAG"),
    (re.compile(r"\biocl\b", re.IGNORECASE), "IOCL"),
    (re.compile(r"\bbpcl\b", re.IGNORECASE), "BPCL"),
    (re.compile(r"\bhpcl\b", re.IGNORECASE), "HPCL"),
    (re.compile(r"airtel", re.IGNORECASE), "AIRTEL"),
    (re.compile(r"\bjio\b", re.IGNORECASE), "JIO"),
    (re.compile(r"\bvi\b|vodafone|idea", re.IGNORECASE), "VI"),
    (re.compile(r"bsnl", re.IGNORECASE), "BSNL"),
    (re.compile(r"groww", re.IGNORECASE), "GROWW"),
    (re.compile(r"zerodha", re.IGNORECASE), "ZERODHA"),
    (re.compile(r"upstox", re.IGNORECASE), "UPSTOX"),
    (re.compile(r"\bcams\b", re.IGNORECASE), "CAMS"),
    (re.compile(r"kfintech", re.IGNORECASE), "KFINTECH"),
    (re.compile(r"\blic\b", re.IGNORECASE), "LIC"),
    (re.compile(r"hdfc\s*life", re.IGNORECASE), "HDFC LIFE"),
    (re.compile(r"policybazaar", re.IGNORECASE), "POLICYBAZAAR"),
    (re.compile(r"atm\s*wdl|nfs.?cash|cash\s*withdrawal", re.IGNORECASE), "ATM WITHDRAWAL"),
]

# Date formats to try when parsing RawTransaction.date strings
_DATE_FORMATS = [
    "%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y",
    "%d/%m/%y", "%d-%m-%y",
    "%d %b %Y", "%d %B %Y",
    "%Y/%m/%d",
]


@dataclass
class CleanResult:
    transactions: list[Transaction]
    dropped_count: int
    duplicate_count: int
    drop_reasons: list[str]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def clean(raw_transactions: list[RawTransaction]) -> CleanResult:
    """Clean and normalize raw transactions into canonical Transaction records."""
    transactions: list[Transaction] = []
    dropped_count = 0
    duplicate_count = 0
    drop_reasons: list[str] = []
    seen_hashes: set[str] = set()

    for raw in raw_transactions:
        # 1. Date normalization
        parsed_date = _parse_date(raw.date)
        if parsed_date is None:
            dropped_count += 1
            drop_reasons.append(f"Row {raw.source_row}: unparseable date '{raw.date}'")
            continue

        # 2. Amount resolution
        amount, txn_type = _resolve_amount(raw)
        if amount is None or amount == 0:
            dropped_count += 1
            drop_reasons.append(f"Row {raw.source_row}: zero or missing amount")
            continue

        # 3. Description cleanup
        desc_clean = _clean_description(raw.description)

        # 4. Merchant extraction
        merchant = _extract_merchant(raw.description, desc_clean)

        # 5. Deduplication
        dedup_hash = _make_hash(parsed_date, amount, desc_clean)
        is_duplicate = dedup_hash in seen_hashes
        if is_duplicate:
            duplicate_count += 1
        else:
            seen_hashes.add(dedup_hash)

        txn = Transaction(
            id=str(uuid.uuid4()),
            date=parsed_date,
            description_raw=raw.description,
            description_clean=desc_clean,
            amount=amount,
            type=txn_type,
            merchant=merchant,
            category=None,
            category_confidence=0.0,
            is_recurring=False,
            is_duplicate=is_duplicate,
            recurring_group_id=None,
            metadata={
                "source_row": raw.source_row,
                "balance": raw.balance,
                "reference": raw.reference,
            },
        )
        transactions.append(txn)

    return CleanResult(
        transactions=transactions,
        dropped_count=dropped_count,
        duplicate_count=duplicate_count,
        drop_reasons=drop_reasons,
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_date(date_str: str | None) -> date_type | None:
    """Parse a date string into a Python date object."""
    if not date_str:
        return None
    s = str(date_str).strip()
    import pandas as pd
    for fmt in _DATE_FORMATS:
        try:
            return pd.to_datetime(s, format=fmt).date()
        except Exception:
            pass
    try:
        return pd.to_datetime(s, dayfirst=True).date()
    except Exception:
        return None


def _resolve_amount(raw: RawTransaction) -> tuple[float | None, str]:
    """Determine the signed amount and transaction type."""
    debit = raw.debit
    credit = raw.credit

    # Both populated: prefer non-zero; if both non-zero, flag debit (edge case P-08)
    if debit and debit > 0 and credit and credit > 0:
        return debit, "debit"

    if debit and debit > 0:
        return round(debit, 2), "debit"
    if credit and credit > 0:
        return round(credit, 2), "credit"

    return None, "debit"


def _clean_description(raw_desc: str) -> str:
    """Normalize a raw transaction description."""
    s = raw_desc.strip()

    # Strip UPI / IMPS / NEFT / RTGS channel boilerplate (but keep counterparty)
    # e.g. "UPI/SWIGGY@ybl-HDFC0001234-123456789012-Payment" → "SWIGGY Payment"
    s = _strip_upi_format(s)

    # Strip POS prefix
    s = _POS_PREFIX.sub("", s)

    # Strip bank branch codes like HDFC0001234, AXIS0000456
    s = _BANK_BRANCH_CODES.sub(" ", s)

    # Strip long numeric reference numbers (also guards PII before any display)
    s = _UPI_REF_NUMBERS.sub(" ", s)

    # Strip phone numbers (Indian mobile numbers)
    s = _PHONE_NUMBERS.sub(" ", s)

    # Strip UPI handles (@paytm, @ybl, etc.)
    s = _UPI_HANDLE.sub(" ", s)

    # Strip card masks
    s = _CARD_MASK.sub(" ", s)

    # Strip channel prefixes (NEFT CR-, SI , etc.)
    s = _CHANNEL_PREFIXES.sub("", s)

    # Normalize remaining separators / dashes between words
    s = re.sub(r"[-/]+", " ", s)

    # Collapse extra whitespace
    s = _EXTRA_WHITESPACE.sub(" ", s).strip()

    # Strip trailing separators
    s = _TRAILING_SEPARATORS.sub("", s).strip()

    if not s:
        s = "Unknown transaction"

    return s


def _strip_upi_format(s: str) -> str:
    """
    Handle the UPI/MERCHANT@handle-BANKCODE-REFNUM-Purpose pattern.
    Extracts the merchant/counterparty name portion.
    e.g. "UPI/SWIGGY@ybl-HDFC0001234-123456789012-Payment" → "SWIGGY Payment"
    e.g. "UPI/RAHUL KUMAR/RENT MAR-YESB0YBLUPI-..." → "RAHUL KUMAR RENT MAR"
    """
    # Match: UPI/<COUNTERPARTY>/<...>-BANKCODE-REF-Purpose  or UPI/<COUNTERPARTY@handle>-...
    m = re.match(r"^UPI/(.+?)(?:-[A-Z]{4}\d{7}|-[A-Z0-9]{7,}|$)", s, re.IGNORECASE)
    if m:
        counterparty = m.group(1)
        # Remove handle from counterparty
        counterparty = _UPI_HANDLE.sub("", counterparty).strip()
        # Remove slash-separated parts after counterparty
        parts = [p.strip() for p in counterparty.split("/") if p.strip()]
        return " ".join(parts)
    # Fallback: just strip the prefix token
    return _UPI_BOILERPLATE.sub("", s)


def _extract_merchant(raw_desc: str, clean_desc: str) -> str | None:
    """Extract a known merchant name from the description."""
    combined = raw_desc.upper() + " " + clean_desc.upper()
    for pattern, merchant_name in _MERCHANT_HINTS:
        if pattern.search(combined):
            return merchant_name
    return None


def _make_hash(txn_date: date_type, amount: float, desc_clean: str) -> str:
    """Create a deduplication hash from (date, amount, normalized_description)."""
    # Normalize description for hashing: uppercase, collapse whitespace
    normalized = re.sub(r"\s+", " ", desc_clean.upper().strip())
    raw = f"{txn_date.isoformat()}|{amount:.2f}|{normalized}"
    return hashlib.md5(raw.encode()).hexdigest()

