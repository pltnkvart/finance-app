from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime, time

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.transaction import TransactionCreate, TransactionUpdate, TransactionResponse
from app.domain.services.transaction_service import TransactionService

router = APIRouter()


@router.get("/", response_model=List[TransactionResponse])
async def get_transactions(
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all transactions with pagination"""
    service = TransactionService(db)
    start_datetime = datetime.combine(start_date, time.min) if start_date else None
    end_datetime = datetime.combine(end_date, time.max) if end_date else None
    transactions = service.get_transactions(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        start_date=start_datetime,
        end_date=end_datetime
    )
    
    return [
        TransactionResponse(
            id=t.id,
            amount=t.amount,
            description=t.description,
            transaction_date=t.transaction_date,
            transaction_type=t.transaction_type,
            category_id=t.category_id,
            category_name=t.category.name if t.category else None,
            account_id=t.account_id,
            account_name=t.account.name if t.account else None,
            created_at=t.created_at,
            updated_at=t.updated_at
        )
        for t in transactions
    ]


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific transaction by ID"""
    service = TransactionService(db)
    transaction = service.get_transaction(transaction_id, current_user.id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return TransactionResponse(
        id=transaction.id,
        amount=transaction.amount,
        description=transaction.description,
        transaction_date=transaction.transaction_date,
        transaction_type=transaction.transaction_type,
        category_id=transaction.category_id,
        category_name=transaction.category.name if transaction.category else None,
        account_id=transaction.account_id,
        account_name=transaction.account.name if transaction.account else None,
        created_at=transaction.created_at,
        updated_at=transaction.updated_at
    )


@router.post("/", response_model=TransactionResponse)
async def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new transaction"""
    service = TransactionService(db)
    try:
        created = service.create_transaction(transaction, current_user.id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Account not found")
    
    return TransactionResponse(
        id=created.id,
        amount=created.amount,
        description=created.description,
        transaction_date=created.transaction_date,
        transaction_type=created.transaction_type,
        category_id=created.category_id,
        category_name=created.category.name if created.category else None,
        account_id=created.account_id,
        account_name=created.account.name if created.account else None,
        created_at=created.created_at,
        updated_at=created.updated_at
    )


@router.put("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: int,
    transaction_update: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a transaction"""
    service = TransactionService(db)
    try:
        transaction = service.update_transaction(transaction_id, transaction_update, current_user.id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Account not found")
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return TransactionResponse(
        id=transaction.id,
        amount=transaction.amount,
        description=transaction.description,
        transaction_date=transaction.transaction_date,
        transaction_type=transaction.transaction_type,
        category_id=transaction.category_id,
        category_name=transaction.category.name if transaction.category else None,
        account_id=transaction.account_id,
        account_name=transaction.account.name if transaction.account else None,
        created_at=transaction.created_at,
        updated_at=transaction.updated_at
    )


@router.delete("/{transaction_id}")
async def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a transaction"""
    service = TransactionService(db)
    success = service.delete_transaction(transaction_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"message": "Transaction deleted successfully"}


@router.post("/bulk-categorize")
async def bulk_categorize_transactions(
    category_id: int,
    transaction_ids: List[int],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Bulk update category for multiple transactions"""
    service = TransactionService(db)
    count = service.bulk_categorize(category_id, transaction_ids, current_user.id)
    return {"message": f"Updated {count} transactions"}
