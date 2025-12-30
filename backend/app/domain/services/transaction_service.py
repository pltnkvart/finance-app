from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from app.models.transaction import Transaction
from app.models.category import Category
from app.schemas.transaction import TransactionCreate, TransactionUpdate
from app.domain.services.categorization_service import CategorizationService


class TransactionService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_transactions(self, skip: int = 0, limit: int = 100) -> List[Transaction]:
        """Get all transactions with pagination"""
        return self.db.query(Transaction).order_by(
            Transaction.transaction_date.desc()
        ).offset(skip).limit(limit).all()
    
    def get_transaction(self, transaction_id: int) -> Optional[Transaction]:
        """Get a transaction by ID"""
        return self.db.query(Transaction).filter(Transaction.id == transaction_id).first()
    
    def create_transaction(self, transaction: TransactionCreate) -> Transaction:
        """Create a new transaction"""
        db_transaction = Transaction(**transaction.model_dump())
        self.db.add(db_transaction)
        self.db.commit()
        self.db.refresh(db_transaction)
        return db_transaction
    
    def update_transaction(
        self, 
        transaction_id: int, 
        transaction_update: TransactionUpdate
    ) -> Optional[Transaction]:
        """Update a transaction"""
        db_transaction = self.get_transaction(transaction_id)
        if not db_transaction:
            return None
        
        # Track category change for learning
        old_category_id = db_transaction.category_id
        
        update_data = transaction_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_transaction, key, value)
        
        self.db.commit()
        self.db.refresh(db_transaction)
        
        # If category changed, learn from it
        if 'category_id' in update_data and update_data['category_id'] != old_category_id:
            categorization_service = CategorizationService(self.db)
            categorization_service.learn_from_correction(
                transaction_id=transaction_id,
                old_category_id=old_category_id,
                new_category_id=update_data['category_id'],
                description=db_transaction.description
            )
        
        return db_transaction
    
    def delete_transaction(self, transaction_id: int) -> bool:
        """Delete a transaction"""
        db_transaction = self.get_transaction(transaction_id)
        if not db_transaction:
            return False
        
        self.db.delete(db_transaction)
        self.db.commit()
        return True
    
    def bulk_categorize(self, category_id: int, transaction_ids: List[int]) -> int:
        """Bulk update category for multiple transactions"""
        count = self.db.query(Transaction).filter(
            Transaction.id.in_(transaction_ids)
        ).update(
            {Transaction.category_id: category_id},
            synchronize_session=False
        )
        self.db.commit()
        return count
