from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=72)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TelegramLinkCodeResponse(BaseModel):
    code: str
    expires_at: datetime
