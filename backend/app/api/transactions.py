from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.transaction import TransactionCreate, TransactionUpdate, TransactionResponse
from app.domain.services.transaction_service import TransactionService

router = APIRouter()


@router.get("/", response_model=List[TransactionResponse])
async def get_transactions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all transactions with pagination"""
    service = TransactionService(db)
    transactions = service.get_transactions(skip=skip, limit=limit)
    
    return [
        TransactionResponse(
            id=t.id,
            amount=t.amount,
            description=t.description,
            transaction_date=t.transaction_date,
            category_id=t.category_id,
            category_name=t.category.name if t.category else None,
            created_at=t.created_at,
            updated_at=t.updated_at
        )
        for t in transactions
    ]


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific transaction by ID"""
    service = TransactionService(db)
    transaction = service.get_transaction(transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return TransactionResponse(
        id=transaction.id,
        amount=transaction.amount,
        description=transaction.description,
        transaction_date=transaction.transaction_date,
        category_id=transaction.category_id,
        category_name=transaction.category.name if transaction.category else None,
        created_at=transaction.created_at,
        updated_at=transaction.updated_at
    )


@router.post("/", response_model=TransactionResponse)
async def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db)
):
    """Create a new transaction"""
    service = TransactionService(db)
    created = service.create_transaction(transaction)
    
    return TransactionResponse(
        id=created.id,
        amount=created.amount,
        description=created.description,
        transaction_date=created.transaction_date,
        category_id=created.category_id,
        category_name=created.category.name if created.category else None,
        created_at=created.created_at,
        updated_at=created.updated_at
    )


@router.put("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: int,
    transaction_update: TransactionUpdate,
    db: Session = Depends(get_db)
):
    """Update a transaction"""
    service = TransactionService(db)
    transaction = service.update_transaction(transaction_id, transaction_update)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return TransactionResponse(
        id=transaction.id,
        amount=transaction.amount,
        description=transaction.description,
        transaction_date=transaction.transaction_date,
        category_id=transaction.category_id,
        category_name=transaction.category.name if transaction.category else None,
        created_at=transaction.created_at,
        updated_at=transaction.updated_at
    )


@router.delete("/{transaction_id}")
async def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db)
):
    """Delete a transaction"""
    service = TransactionService(db)
    success = service.delete_transaction(transaction_id)
    if not success:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"message": "Transaction deleted successfully"}


@router.post("/bulk-categorize")
async def bulk_categorize_transactions(
    category_id: int,
    transaction_ids: List[int],
    db: Session = Depends(get_db)
):
    """Bulk update category for multiple transactions"""
    service = TransactionService(db)
    count = service.bulk_categorize(category_id, transaction_ids)
    return {"message": f"Updated {count} transactions"}
