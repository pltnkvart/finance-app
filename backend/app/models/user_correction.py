from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class UserCorrection(Base):
    __tablename__ = "user_corrections"
    
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False, index=True)
    old_category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    new_category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    
    # Timestamp
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    transaction = relationship("Transaction")
    old_category = relationship("Category", foreign_keys=[old_category_id])
    new_category = relationship("Category", foreign_keys=[new_category_id])
