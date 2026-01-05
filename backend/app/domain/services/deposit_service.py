from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.models.deposit import Deposit, DepositStatus
from app.schemas.deposit import DepositCreate, DepositUpdate


class DepositService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_deposits(self, account_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[Deposit]:
        """Получить список вкладов"""
        query = self.db.query(Deposit)
        if account_id:
            query = query.filter(Deposit.account_id == account_id)
        return query.offset(skip).limit(limit).all()
    
    def get_deposit(self, deposit_id: int) -> Optional[Deposit]:
        """Получить вклад по ID"""
        return self.db.query(Deposit).filter(Deposit.id == deposit_id).first()
    
    def create_deposit(self, deposit_data: DepositCreate) -> Deposit:
        """Создать новый вклад"""
        deposit = Deposit(
            account_id=deposit_data.account_id,
            name=deposit_data.name,
            amount=deposit_data.amount,
            interest_rate=deposit_data.interest_rate,
            start_date=deposit_data.start_date,
            end_date=deposit_data.end_date,
            status=DepositStatus.ACTIVE
        )
        self.db.add(deposit)
        self.db.commit()
        self.db.refresh(deposit)
        return deposit
    
    def update_deposit(self, deposit_id: int, deposit_data: DepositUpdate) -> Optional[Deposit]:
        """Обновить вклад"""
        deposit = self.get_deposit(deposit_id)
        if not deposit:
            return None
        
        update_data = deposit_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(deposit, key, value)
        
        self.db.commit()
        self.db.refresh(deposit)
        return deposit
    
    def delete_deposit(self, deposit_id: int) -> bool:
        """Удалить вклад"""
        deposit = self.get_deposit(deposit_id)
        if not deposit:
            return False
        
        self.db.delete(deposit)
        self.db.commit()
        return True
    
    def close_deposit(self, deposit_id: int) -> Optional[Deposit]:
        """Закрыть вклад"""
        deposit = self.get_deposit(deposit_id)
        if not deposit:
            return None
        
        deposit.status = DepositStatus.COMPLETED
        self.db.commit()
        self.db.refresh(deposit)
        return deposit
