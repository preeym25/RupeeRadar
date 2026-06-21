"""Groq LLM fallback categorizer for low-confidence transactions (Phase 5)."""

import json
import logging
from typing import Any

from app.models.transaction import Category, Transaction
from app.llm.groq_client import get_groq_client
from app.settings import get_settings

logger = logging.getLogger(__name__)


def categorize_with_llm(transactions: list[Transaction]) -> list[Transaction]:
    """Fallback categorizer that calls Groq LLM for low-confidence transactions."""
    client = get_groq_client()
    settings = get_settings()
    
    if not client:
        logger.warning("LLM Categorization skipped: Groq client not configured or disabled.")
        return transactions

    # Filter low confidence debit transactions
    to_categorize = [t for t in transactions if t.category_confidence < 0.8 and t.type == "debit"]
    if not to_categorize:
        return transactions
    
    # Process in batches to stay within token limits
    batch_size = 50
    for i in range(0, len(to_categorize), batch_size):
        batch = to_categorize[i:i + batch_size]
        _process_batch(client, settings.groq_model, batch)
        
    return transactions


def _process_batch(client: Any, model: str, batch: list[Transaction]) -> None:
    categories = [c.value for c in Category]
    
    items = []
    for t in batch:
        items.append({
            "id": t.id,
            "description": t.description_clean or t.description_raw,
            "amount": t.amount
        })

    system_prompt = f"""You are a bank transaction categorizer for Indian bank statements.
Given a list of transactions, return a JSON object mapping each transaction 'id' to the best fitting category string.
Allowed categories: {categories}
If unsure, return "Other".

Return ONLY a valid JSON object of the format:
{{ "results": {{ "tx_id_1": "Category", "tx_id_2": "Category" }} }}
"""
    
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(items)}
            ],
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        
        content = completion.choices[0].message.content
        if not content:
            return
            
        data = json.loads(content)
        results = data.get("results", {})
        
        for t in batch:
            cat_val = results.get(t.id)
            if cat_val in categories:
                t.category = Category(cat_val)
                t.category_confidence = 0.85
                t.metadata["source"] = "llm"
                
    except Exception:
        logger.exception("Error during LLM batch categorization.")

