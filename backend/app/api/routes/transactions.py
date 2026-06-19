"""Transaction management API routes."""

from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import os
import tempfile
from typing import List

from app.database import get_db
from app.models.transaction import Transaction as TransactionSchema, Category
from app.models.database_models import Transaction as DBTransaction, Statement, User
from app.services.parser import TransactionParser
from app.services.cleaner import TransactionCleaner
from app.services.categorizer import TransactionCategorizer

router = APIRouter(prefix="/api/v1/transactions", tags=["transactions"])


@router.post("/upload")
async def upload_statement(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and process bank statement.
    
    Supports: CSV, Excel, PDF formats
    """
    try:
        # Validate file size (max 50MB)
        MAX_FILE_SIZE = 50 * 1024 * 1024
        
        file_content = await file.read()
        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Max: 50MB, Got: {len(file_content)/(1024*1024):.1f}MB"
            )
        
        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(file_content)
            tmp_path = tmp.name
        
        try:
            # Parse transactions
            file_type = file.filename.split('.')[-1].lower()
            parser = TransactionParser()
            raw_transactions = parser.auto_detect_format(tmp_path, file_type)
            
            if not raw_transactions:
                raise HTTPException(status_code=400, detail="No transactions found in file")
            
            # Clean transactions
            cleaner = TransactionCleaner()
            cleaned = [cleaner.clean_transaction(t) for t in raw_transactions]
            
            # Categorize
            categorizer = TransactionCategorizer()
            categorized = [categorizer.categorize_transaction(t) for t in cleaned]
            
            # Create statement record
            statement = Statement(
                user_id=1,  # TODO: Get from authenticated user
                file_name=file.filename,
                total_transactions=len(categorized),
                processing_status="completed"
            )
            db.add(statement)
            db.flush()
            
            # Save transactions to database
            for trans in categorized:
                db_transaction = DBTransaction(
                    user_id=1,
                    statement_id=statement.id,
                    transaction_date=trans.get('date'),
                    amount=trans.get('amount'),
                    raw_description=trans.get('description'),
                    cleaned_description=trans.get('cleaned_description'),
                    category=trans.get('category'),
                    merchant_name=trans.get('merchant_name'),
                    transaction_type=trans.get('type'),
                    category_confidence=trans.get('category_confidence', 0.0)
                )
                db.add(db_transaction)
            
            db.commit()
            
            return {
                "status": "success",
                "statement_id": statement.id,
                "transactions_count": len(categorized),
                "message": f"Successfully processed {len(categorized)} transactions"
            }
        
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Processing failed: {str(e)}")


@router.get("/", response_model=List[TransactionSchema])
async def get_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: str = Query(None),
    db: Session = Depends(get_db)
):
    """Get all transactions for the current user with pagination."""
    query = db.query(DBTransaction).filter(DBTransaction.user_id == 1)
    
    if category:
        query = query.filter(DBTransaction.category == category)
    
    transactions = query.offset(skip).limit(limit).all()
    
    return [
        TransactionSchema(
            id=str(t.id),
            date=t.transaction_date.date(),
            description_raw=t.raw_description,
            description_clean=t.cleaned_description,
            amount=t.amount,
            type="debit" if t.transaction_type == "DEBIT" else "credit",
            merchant=t.merchant_name,
            category=t.category,
            category_confidence=t.category_confidence,
            is_recurring=t.is_recurring
        )
        for t in transactions
    ]


@router.get("/categories")
async def get_categories():
    """Get available transaction categories."""
    return {
        "categories": [c.value for c in Category]
    }


@router.get("/stats")
async def get_transaction_stats(
    db: Session = Depends(get_db)
):
    """Get transaction statistics."""
    transactions = db.query(DBTransaction).filter(
        DBTransaction.user_id == 1
    ).all()
    
    if not transactions:
        return {"error": "No transactions found"}
    
    # Calculate statistics
    total_income = sum([t.amount for t in transactions if t.transaction_type == 'CREDIT'])
    total_spend = sum([t.amount for t in transactions if t.transaction_type == 'DEBIT'])
    savings = total_income - total_spend
    
    # Category breakdown
    category_spend = {}
    for trans in transactions:
        if trans.transaction_type == 'DEBIT':
            cat = trans.category.value if trans.category else 'Other'
            category_spend[cat] = category_spend.get(cat, 0) + trans.amount
    
    return {
        'total_income': total_income,
        'total_spend': total_spend,
        'savings': savings,
        'savings_rate': (savings / total_income * 100) if total_income > 0 else 0,
        'category_breakdown': category_spend,
        'transaction_count': len(transactions)
    }


@router.get("/{transaction_id}")
async def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific transaction by ID."""
    transaction = db.query(DBTransaction).filter(
        DBTransaction.id == transaction_id,
        DBTransaction.user_id == 1
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return TransactionSchema(
        id=str(transaction.id),
        date=transaction.transaction_date.date(),
        description_raw=transaction.raw_description,
        description_clean=transaction.cleaned_description,
        amount=transaction.amount,
        type="debit" if transaction.transaction_type == "DEBIT" else "credit",
        merchant=transaction.merchant_name,
        category=transaction.category,
        category_confidence=transaction.category_confidence,
        is_recurring=transaction.is_recurring
    )


@router.put("/{transaction_id}/category")
async def update_transaction_category(
    transaction_id: int,
    category: str,
    db: Session = Depends(get_db)
):
    """Update category for a transaction."""
    transaction = db.query(DBTransaction).filter(
        DBTransaction.id == transaction_id,
        DBTransaction.user_id == 1
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    try:
        transaction.category = Category[category.upper()]
        db.commit()
        return {"status": "success", "message": "Category updated"}
    except KeyError:
        raise HTTPException(status_code=400, detail=f"Invalid category: {category}")
