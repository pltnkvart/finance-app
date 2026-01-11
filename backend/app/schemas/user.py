from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=72)


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    telegram_user_id: Optional[str] = None
    telegram_username: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
