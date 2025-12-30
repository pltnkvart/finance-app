from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
from typing import Optional, Dict, Any

from app.models.transaction import Transaction
from app.models.category import Category


class StatisticsService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_summary(
        self, 
        start_date: Optional[date] = None, 
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Get overall transaction summary"""
        query = self.db.query(Transaction)
        
        if start_date:
            query = query.filter(Transaction.transaction_date >= start_date)
        if end_date:
            query = query.filter(Transaction.transaction_date <= end_date)
        
        total = query.with_entities(func.sum(Transaction.amount)).scalar() or 0
        count = query.count()
        
        return {
            "total_amount": float(total),
            "transaction_count": count,
            "start_date": start_date,
            "end_date": end_date
        }
    
    def get_by_category(
        self, 
        start_date: Optional[date] = None, 
        end_date: Optional[date] = None
    ) -> list:
        """Get spending grouped by category"""
        query = self.db.query(
            Category.name,
            func.sum(Transaction.amount).label("total"),
            func.count(Transaction.id).label("count")
        ).join(Transaction, Category.id == Transaction.category_id)
        
        if start_date:
            query = query.filter(Transaction.transaction_date >= start_date)
        if end_date:
            query = query.filter(Transaction.transaction_date <= end_date)
        
        query = query.group_by(Category.name)
        
        return [
            {
                "category": row.name,
                "total": float(row.total),
                "count": row.count
            }
            for row in query.all()
        ]
