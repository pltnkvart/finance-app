from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
import csv
import io

from app.models.transaction import Transaction
from app.models.category import Category


class ExportService:
    def __init__(self, db: Session):
        self.db = db
    
    def export_to_csv(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        category_id: Optional[int] = None
    ) -> str:
        """Export transactions to CSV format"""
        # Build query
        query = self.db.query(
            Transaction.id,
            Transaction.transaction_date,
            Transaction.amount,
            Transaction.description,
            Category.name.label("category")
        ).outerjoin(Category, Transaction.category_id == Category.id)
        
        # Apply filters
        if start_date:
            query = query.filter(Transaction.transaction_date >= start_date)
        if end_date:
            query = query.filter(Transaction.transaction_date <= end_date)
        if category_id:
            query = query.filter(Transaction.category_id == category_id)
        
        # Order by date
        query = query.order_by(Transaction.transaction_date.desc())
        
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(["ID", "Date", "Amount", "Description", "Category"])
        
        # Write data
        for row in query.all():
            writer.writerow([
                row.id,
                row.transaction_date.strftime("%Y-%m-%d %H:%M:%S"),
                float(row.amount),
                row.description,
                row.category or "Uncategorized"
            ])
        
        return output.getvalue()
