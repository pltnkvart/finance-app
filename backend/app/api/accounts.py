from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.account import AccountCreate, AccountUpdate, AccountResponse
from app.domain.services.account_service import AccountService

router = APIRouter()


@router.get("/", response_model=List[AccountResponse])
async def get_accounts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить все счета"""
    service = AccountService(db)
    accounts = service.get_accounts(current_user.id, skip=skip, limit=limit)
    return accounts


@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить конкретный счет по ID"""
    service = AccountService(db)
    account = service.get_account(account_id, current_user.id)
    if not account:
        raise HTTPException(status_code=404, detail="Счет не найден")
    return account


@router.post("/", response_model=AccountResponse)
async def create_account(
    account: AccountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Создать новый счет"""
    service = AccountService(db)
    created = service.create_account(current_user.id, account)
    return created


@router.put("/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: int,
    account_update: AccountUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обновить счет"""
    service = AccountService(db)
    account = service.update_account(account_id, current_user.id, account_update)
    if not account:
        raise HTTPException(status_code=404, detail="Счет не найден")
    return account


@router.delete("/{account_id}")
async def delete_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Удалить счет"""
    service = AccountService(db)
    success = service.delete_account(account_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Счет не найден")
    return {"message": "Счет успешно удален"}
