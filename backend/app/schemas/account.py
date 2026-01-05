from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from decimal import Decimal


class AccountBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    account_type: str  # checking, savings, credit_card, cash, investment
    currency: str = Field(default="RUB", max_length=3)


class AccountCreate(AccountBase):
    balance: Decimal = Field(default=Decimal("0.00"), ge=0)


class AccountUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    account_type: Optional[str] = None
    balance: Optional[Decimal] = Field(None, ge=0)


class AccountResponse(AccountBase):
    id: int
    balance: Decimal
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
