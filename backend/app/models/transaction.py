from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    description = Column(String(500), nullable=False)
    transaction_date = Column(DateTime, nullable=False)
    
    # Foreign key to category
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    
    # Telegram metadata
    telegram_message_id = Column(Integer, nullable=True)
    raw_text = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    category = relationship("Category", back_populates="transactions")
