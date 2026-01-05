from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Enum, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class DepositStatus(str, enum.Enum):
    ACTIVE = "active"  # Активный
    COMPLETED = "completed"  # Завершенный
    CANCELLED = "cancelled"  # Отменен


class Deposit(Base):
    __tablename__ = "deposits"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    interest_rate = Column(Numeric(5, 2), nullable=False)  # Процентная ставка (например, 5.50 для 5.5%)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(Enum(DepositStatus), nullable=False, default=DepositStatus.ACTIVE)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    account = relationship("Account", back_populates="deposits")
