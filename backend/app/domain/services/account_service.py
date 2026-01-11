from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal

from app.models.account import Account
from app.schemas.account import AccountCreate, AccountUpdate


class AccountService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_accounts(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Account]:
        """Получить список счетов"""
        return self.db.query(Account).filter(Account.user_id == user_id).offset(skip).limit(limit).all()
    
    def get_account(self, account_id: int, user_id: int) -> Optional[Account]:
        """Получить счет по ID"""
        return self.db.query(Account).filter(Account.id == account_id, Account.user_id == user_id).first()
    
    def create_account(self, user_id: int, account_data: AccountCreate) -> Account:
        """Создать новый счет"""
        account = Account(
            user_id=user_id,
            name=account_data.name,
            description=account_data.description,
            account_type=account_data.account_type,
            currency=account_data.currency,
            balance=account_data.balance
        )
        self.db.add(account)
        self.db.commit()
        self.db.refresh(account)
        return account
    
    def update_account(self, account_id: int, user_id: int, account_data: AccountUpdate) -> Optional[Account]:
        """Обновить счет"""
        account = self.get_account(account_id, user_id)
        if not account:
            return None
        
        update_data = account_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(account, key, value)
        
        self.db.commit()
        self.db.refresh(account)
        return account
    
    def delete_account(self, account_id: int, user_id: int) -> bool:
        """Удалить счет"""
        account = self.get_account(account_id, user_id)
        if not account:
            return False
        
        self.db.delete(account)
        self.db.commit()
        return True
    
    def get_total_balance(self, user_id: int) -> Decimal:
        """Рассчитать общий баланс по всем счетам"""
        from sqlalchemy import func
        result = self.db.query(func.sum(Account.balance)).filter(Account.user_id == user_id).scalar()
        return Decimal(result) if result else Decimal("0.00")
