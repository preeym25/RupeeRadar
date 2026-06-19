"""Rule-based transaction categorizer (Phase 1)."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from app.models.transaction import Category, Transaction

# Path to merchant rules config
_RULES_PATH = Path(__file__).parent.parent.parent / "config" / "merchant_rules.json"


def _load_rules() -> list[dict[str, Any]]:
    """Load and compile categorization rules from merchant_rules.json."""
    with open(_RULES_PATH, encoding="utf-8") as f:
        data = json.load(f)
    rules = []
    for rule in data.get("rules", []):
        compiled_patterns = [
            re.compile(re.escape(p), re.IGNORECASE)
            for p in rule["patterns"]
        ]
        rules.append({
            "patterns": compiled_patterns,
            "raw_patterns": rule["patterns"],
            "category": rule["category"],
            "confidence": float(rule.get("confidence", 0.8)),
        })
    return rules


# Compile rules at module load time (fast)
_RULES: list[dict[str, Any]] = _load_rules()

# Credit-side income signals: these indicate a Salary/income credit
_SALARY_PATTERNS = re.compile(
    r"(salary|payroll|neft\s*cr|neft\s*credit|stipend|wage)",
    re.IGNORECASE,
)
_INCOME_PATTERNS = re.compile(
    r"(freelance|project\s*payment|bonus|reimbursement|refund|cashback|interest|dividend)",
    re.IGNORECASE,
)


def _match_rules(text: str) -> tuple[Category | None, float]:
    """
    Match a string against all rules.
    Returns (Category, confidence) for the best match, or (None, 0.0).
    Longer / more specific pattern matches win (length as a proxy for specificity).
    """
    best_category: Category | None = None
    best_confidence: float = 0.0
    best_match_len: int = 0

    for rule in _RULES:
        for pattern in rule["patterns"]:
            m = pattern.search(text)
            if m:
                match_len = len(m.group(0))
                confidence = rule["confidence"]
                # Prefer longer (more specific) match; break ties by higher confidence
                if match_len > best_match_len or (
                    match_len == best_match_len and confidence > best_confidence
                ):
                    best_match_len = match_len
                    best_confidence = confidence
                    try:
                        best_category = Category(rule["category"])
                    except ValueError:
                        best_category = Category.OTHER

    return best_category, best_confidence


def _categorize_single(txn: Transaction) -> Transaction:
    """Assign category and confidence to a single Transaction."""
    # Build combined search text from clean desc + raw desc + merchant
    parts = [txn.description_clean, txn.description_raw]
    if txn.merchant:
        parts.append(txn.merchant)
    search_text = " ".join(parts)

    # --- Credit-side rules first ---
    if txn.type == "credit":
        if _SALARY_PATTERNS.search(search_text):
            return txn.model_copy(update={"category": Category.SALARY, "category_confidence": 0.9})
        # Other credits (cashback, refund, interest) → Other unless rule matches
        category, confidence = _match_rules(search_text)
        if category and confidence >= 0.5:
            return txn.model_copy(update={"category": category, "category_confidence": confidence})
        # Generic credit with no specific rule
        return txn.model_copy(update={"category": Category.OTHER, "category_confidence": 0.3})

    # --- Debit-side rules ---
    category, confidence = _match_rules(search_text)

    if category is None or confidence < 0.5:
        # Fallback: Other with zero confidence
        return txn.model_copy(update={"category": Category.OTHER, "category_confidence": 0.0})

    return txn.model_copy(update={"category": category, "category_confidence": confidence})


def categorize(transactions: list[Transaction]) -> list[Transaction]:
    """Apply rule-based categorization to all transactions."""
    return [_categorize_single(t) for t in transactions]


def reload_rules() -> None:
    """Reload rules from disk (useful for testing)."""
    global _RULES
    _RULES = _load_rules()

