from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional
from decimal import Decimal


class DepositBase(BaseModel):
    name: str = Field(..., max_length=100)
    amount: Decimal = Field(..., ge=0)
    interest_rate: Decimal = Field(..., ge=0, le=100)  # 0-100%
    start_date: date
    end_date: date


class DepositCreate(DepositBase):
    account_id: int


class DepositUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    amount: Optional[Decimal] = Field(None, ge=0)
    interest_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    end_date: Optional[date] = None
    status: Optional[str] = None  # active, completed, cancelled


class DepositResponse(DepositBase):
    id: int
    account_id: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
