from pydantic import BaseModel
from typing import Optional


class TelegramMessageRequest(BaseModel):
    message_id: int
    text: str
    user_id: int
    username: Optional[str] = None


class TelegramMessageResponse(BaseModel):
    success: bool
    transaction_id: Optional[int] = None
    message: str
    parsed_data: Optional[dict] = None
