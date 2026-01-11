from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.deposit import DepositCreate, DepositUpdate, DepositResponse
from app.domain.services.deposit_service import DepositService, InsufficientFundsError

router = APIRouter()


@router.get("/", response_model=List[DepositResponse])
async def get_deposits(
    account_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить все вклады, опционально фильтруя по счету"""
    service = DepositService(db)
    deposits = service.get_deposits(
        user_id=current_user.id,
        account_id=account_id,
        skip=skip,
        limit=limit
    )
    return deposits


@router.get("/{deposit_id}", response_model=DepositResponse)
async def get_deposit(
    deposit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить конкретный вклад по ID"""
    service = DepositService(db)
    deposit = service.get_deposit(deposit_id, current_user.id)
    if not deposit:
        raise HTTPException(status_code=404, detail="Вклад не найден")
    return deposit


@router.post("/", response_model=DepositResponse)
async def create_deposit(
    deposit: DepositCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Создать новый вклад"""
    service = DepositService(db)
    try:
        created = service.create_deposit(deposit, current_user.id)
    except InsufficientFundsError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except ValueError:
        raise HTTPException(status_code=404, detail="Счет не найден")
    return created


@router.put("/{deposit_id}", response_model=DepositResponse)
async def update_deposit(
    deposit_id: int,
    deposit_update: DepositUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обновить вклад"""
    service = DepositService(db)
    try:
        deposit = service.update_deposit(deposit_id, deposit_update, current_user.id)
    except InsufficientFundsError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except ValueError:
        raise HTTPException(status_code=404, detail="Счет не найден")
    if not deposit:
        raise HTTPException(status_code=404, detail="Вклад не найден")
    return deposit


@router.delete("/{deposit_id}")
async def delete_deposit(
    deposit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Удалить вклад"""
    service = DepositService(db)
    success = service.delete_deposit(deposit_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Вклад не найден")
    return {"message": "Вклад успешно удален"}


@router.post("/{deposit_id}/close")
async def close_deposit(
    deposit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Закрыть вклад (установить статус completed)"""
    service = DepositService(db)
    deposit = service.close_deposit(deposit_id, current_user.id)
    if not deposit:
        raise HTTPException(status_code=404, detail="Вклад не найден")
    return deposit
