from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

from app.models.transaction import Transaction, TransactionType
from app.models.account import Account
from app.schemas.transaction import TransactionCreate, TransactionUpdate


class TransactionService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_transactions(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Transaction]:
        """Get all transactions with pagination"""
        query = self.db.query(Transaction).filter(Transaction.user_id == user_id)

        if start_date:
            query = query.filter(Transaction.transaction_date >= start_date)
        if end_date:
            query = query.filter(Transaction.transaction_date <= end_date)

        return query.order_by(
            Transaction.transaction_date.desc()
        ).offset(skip).limit(limit).all()
    
    def get_transaction(self, transaction_id: int, user_id: int) -> Optional[Transaction]:
        """Get a transaction by ID"""
        return self.db.query(Transaction).filter(
            Transaction.id == transaction_id,
            Transaction.user_id == user_id
        ).first()
    
    def create_transaction(self, transaction: TransactionCreate, user_id: Optional[int] = None) -> Transaction:
        """Create a new transaction"""
        if user_id and transaction.account_id:
            if not self._get_account_for_user(transaction.account_id, user_id):
                raise ValueError("Account not found")
        db_transaction = Transaction(**transaction.model_dump(), user_id=user_id)
        self.db.add(db_transaction)
        self._apply_account_balance_on_create(db_transaction)
        self.db.commit()
        self.db.refresh(db_transaction)
        return db_transaction
    
    def update_transaction(
        self, 
        transaction_id: int, 
        transaction_update: TransactionUpdate,
        user_id: int
    ) -> Optional[Transaction]:
        """Update a transaction"""
        db_transaction = self.get_transaction(transaction_id, user_id)
        if not db_transaction:
            return None
        
        old_account_id = db_transaction.account_id
        old_amount = Decimal(db_transaction.amount)
        old_type = db_transaction.transaction_type
        
        update_data = transaction_update.model_dump(exclude_unset=True)
        if "account_id" in update_data and update_data["account_id"]:
            if not self._get_account_for_user(update_data["account_id"], user_id):
                raise ValueError("Account not found")
        for key, value in update_data.items():
            setattr(db_transaction, key, value)

        self._apply_account_balance_on_update(
            old_account_id=old_account_id,
            old_amount=old_amount,
            old_type=old_type,
            new_account_id=db_transaction.account_id,
            new_amount=Decimal(db_transaction.amount),
            new_type=db_transaction.transaction_type
        )

        self.db.commit()
        self.db.refresh(db_transaction)

        return db_transaction
    
    def delete_transaction(self, transaction_id: int, user_id: int) -> bool:
        """Delete a transaction"""
        db_transaction = self.get_transaction(transaction_id, user_id)
        if not db_transaction:
            return False

        self._apply_account_balance_on_delete(db_transaction)
        self.db.delete(db_transaction)
        self.db.commit()
        return True
    
    def bulk_categorize(self, category_id: int, transaction_ids: List[int], user_id: int) -> int:
        """Bulk update category for multiple transactions"""
        count = self.db.query(Transaction).filter(
            Transaction.id.in_(transaction_ids),
            Transaction.user_id == user_id
        ).update(
            {Transaction.category_id: category_id},
            synchronize_session=False
        )
        self.db.commit()
        return count

    def _get_account_for_user(self, account_id: int, user_id: int) -> Optional[Account]:
        return self.db.query(Account).filter(Account.id == account_id, Account.user_id == user_id).first()

    def _apply_account_balance_on_create(self, transaction: Transaction) -> None:
        if not transaction.account_id:
            return

        account = self.db.query(Account).filter(Account.id == transaction.account_id).first()
        if not account:
            return

        if transaction.transaction_type == TransactionType.INCOME:
            account.balance = Decimal(account.balance) + Decimal(transaction.amount)
        else:
            account.balance = Decimal(account.balance) - Decimal(transaction.amount)

    def _apply_account_balance_on_update(
        self,
        old_account_id: Optional[int],
        old_amount: Decimal,
        old_type: TransactionType,
        new_account_id: Optional[int],
        new_amount: Decimal,
        new_type: TransactionType
    ) -> None:
        if old_account_id == new_account_id:
            if not old_account_id:
                return

            account = self.db.query(Account).filter(Account.id == old_account_id).first()
            if not account:
                return

            old_effect = old_amount if old_type == TransactionType.INCOME else -old_amount
            new_effect = new_amount if new_type == TransactionType.INCOME else -new_amount
            delta = new_effect - old_effect
            account.balance = Decimal(account.balance) + delta
            return

        if old_account_id:
            old_account = self.db.query(Account).filter(Account.id == old_account_id).first()
            if old_account:
                old_account.balance = Decimal(old_account.balance) - (
                    old_amount if old_type == TransactionType.INCOME else -old_amount
                )

        if new_account_id:
            new_account = self.db.query(Account).filter(Account.id == new_account_id).first()
            if new_account:
                new_account.balance = Decimal(new_account.balance) + (
                    new_amount if new_type == TransactionType.INCOME else -new_amount
                )

    def _apply_account_balance_on_delete(self, transaction: Transaction) -> None:
        if not transaction.account_id:
            return

        account = self.db.query(Account).filter(Account.id == transaction.account_id).first()
        if not account:
            return

        if transaction.transaction_type == TransactionType.INCOME:
            account.balance = Decimal(account.balance) - Decimal(transaction.amount)
        else:
            account.balance = Decimal(account.balance) + Decimal(transaction.amount)
