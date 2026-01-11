from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    telegram_user_id = Column(String(32), unique=True, nullable=True, index=True)
    telegram_username = Column(String(64), nullable=True)
    telegram_link_code = Column(String(32), nullable=True, index=True)
    telegram_link_code_expires_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    accounts = relationship("Account", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    deposits = relationship("Deposit", back_populates="user")
