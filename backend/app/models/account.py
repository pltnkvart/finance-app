from sqlalchemy import Column, Integer, String, Numeric, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class AccountType(str, enum.Enum):
    CHECKING = "checking"  # Текущий счет
    SAVINGS = "savings"  # Накопительный счет
    CREDIT_CARD = "credit_card"  # Кредитная карта
    CASH = "cash"  # Наличные
    INVESTMENT = "investment"  # Инвестиционный счет


class Account(Base):
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    account_type = Column(Enum(AccountType), nullable=False, default=AccountType.CHECKING)
    currency = Column(String(3), nullable=False, default="RUB")
    balance = Column(Numeric(12, 2), nullable=False, default=0.00)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    transactions = relationship("Transaction", back_populates="account")
    deposits = relationship("Deposit", back_populates="account")
