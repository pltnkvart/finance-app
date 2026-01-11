from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, datetime
from typing import Optional, Dict, Any
from decimal import Decimal

from app.models.transaction import Transaction, TransactionType
from app.models.category import Category
from app.models.account import Account
from app.models.deposit import Deposit, DepositStatus


class StatisticsService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_summary(
        self,
        user_id: Optional[int],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get overall transaction summary"""
        query = self.db.query(Transaction)
        if user_id is not None:
            query = query.filter(Transaction.user_id == user_id)
        
        if start_date:
            query = query.filter(Transaction.transaction_date >= start_date)
        if end_date:
            query = query.filter(Transaction.transaction_date <= end_date)
        
        total = query.with_entities(func.sum(Transaction.amount)).scalar() or 0
        count = query.count()

        expense_total = query.filter(Transaction.transaction_type == TransactionType.EXPENSE).with_entities(
            func.sum(Transaction.amount)
        ).scalar() or 0
        income_total = query.filter(Transaction.transaction_type == TransactionType.INCOME).with_entities(
            func.sum(Transaction.amount)
        ).scalar() or 0
        
        total_balance_query = self.db.query(func.sum(Account.balance))
        total_deposits_query = self.db.query(func.sum(Deposit.amount)).filter(
            Deposit.status == DepositStatus.ACTIVE
        )
        if user_id is not None:
            total_balance_query = total_balance_query.filter(Account.user_id == user_id)
            total_deposits_query = total_deposits_query.filter(Deposit.user_id == user_id)
        total_balance = total_balance_query.scalar() or 0
        total_deposits = total_deposits_query.scalar() or 0
        
        return {
            "total_amount": float(expense_total),
            "income_total": float(income_total),
            "expense_total": float(expense_total),
            "transaction_count": count,
            "total_balance": float(total_balance + total_deposits),
            "start_date": start_date,
            "end_date": end_date
        }
    
    def get_by_category(
        self, 
        user_id: int,
        start_date: Optional[datetime] = None, 
        end_date: Optional[datetime] = None
    ) -> list:
        """Get spending grouped by category"""
        category_label = func.coalesce(Category.name, "Без категории")
        query = self.db.query(
            category_label.label("category"),
            func.sum(Transaction.amount).label("total"),
            func.count(Transaction.id).label("count")
        ).outerjoin(Category, Category.id == Transaction.category_id).filter(
            Transaction.transaction_type == TransactionType.EXPENSE,
            Transaction.user_id == user_id
        )
        
        if start_date:
            query = query.filter(Transaction.transaction_date >= start_date)
        if end_date:
            query = query.filter(Transaction.transaction_date <= end_date)
        
        query = query.group_by(category_label)
        
        return [
            {
                "category": row.category,
                "total": float(row.total),
                "count": row.count
            }
            for row in query.all()
        ]

    def get_spending_trend(
        self,
        user_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> list:
        """Get monthly expense totals for trend chart"""
        month_label = func.date_trunc("month", Transaction.transaction_date).label("month")
        query = self.db.query(
            month_label,
            func.sum(Transaction.amount).label("total")
        ).filter(
            Transaction.transaction_type == TransactionType.EXPENSE,
            Transaction.user_id == user_id
        )

        if start_date:
            query = query.filter(Transaction.transaction_date >= start_date)
        if end_date:
            query = query.filter(Transaction.transaction_date <= end_date)

        query = query.group_by(month_label).order_by(month_label.asc())

        return [
            {
                "month": row.month.strftime("%Y-%m"),
                "total": float(row.total),
            }
            for row in query.all()
        ]
