from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal
from typing import Optional


class TransactionBase(BaseModel):
    amount: Decimal = Field(..., description="Transaction amount")
    description: str = Field(..., min_length=1, max_length=500)
    transaction_date: datetime = Field(..., description="Date of transaction")
    category_id: Optional[int] = None


class TransactionCreate(TransactionBase):
    telegram_message_id: Optional[int] = None
    raw_text: Optional[str] = None


class TransactionUpdate(BaseModel):
    amount: Optional[Decimal] = None
    description: Optional[str] = None
    transaction_date: Optional[datetime] = None
    category_id: Optional[int] = None


class TransactionResponse(TransactionBase):
    id: int
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
