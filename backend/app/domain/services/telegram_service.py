from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import re
from datetime import datetime

from app.schemas.telegram import TelegramMessageRequest, TelegramMessageResponse
from app.schemas.transaction import TransactionCreate
from app.domain.services.transaction_service import TransactionService
from app.domain.services.user_service import UserService


class TelegramService:
    def __init__(self, db: Session):
        self.db = db
        self.transaction_service = TransactionService(db)
        self.user_service = UserService(db)
    
    async def parse_and_create_transaction(
        self, 
        message: TelegramMessageRequest
    ) -> TelegramMessageResponse:
        """Parse Telegram message and create transaction"""
        try:
            if message.text.strip().startswith("/link"):
                return await self._handle_link_command(message)

            user = self.user_service.get_by_telegram_id(str(message.user_id))
            if not user:
                return TelegramMessageResponse(
                    success=False,
                    message="Ваш Telegram не привязан. Получите код в веб-интерфейсе и отправьте: /link КОД"
                )

            # Parse the message text
            parsed_data = self._parse_message(message.text)
            
            if not parsed_data:
                return TelegramMessageResponse(
                    success=False,
                    message="Не удалось распознать транзакцию. Используйте формат: '100 продукты' или '50.5 кофе'"
                )
            
            # Create transaction
            transaction_data = TransactionCreate(
                amount=parsed_data["amount"],
                description=parsed_data["description"],
                transaction_date=datetime.now(),
                transaction_type=parsed_data.get("transaction_type", "expense"),
                telegram_message_id=message.message_id,
                raw_text=message.text
            )
            
            transaction = self.transaction_service.create_transaction(transaction_data, user_id=user.id)
            
            return TelegramMessageResponse(
                success=True,
                transaction_id=transaction.id,
                message=f"Транзакция создана: {parsed_data['amount']} ₽ за {parsed_data['description']}",
                parsed_data=parsed_data
            )
            
        except Exception as e:
            return TelegramMessageResponse(
                success=False,
                message=f"Ошибка при создании транзакции: {str(e)}"
            )
    
    def _parse_message(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse transaction from message text"""
        # Pattern 1: "100 groceries" or "+100 salary"
        pattern1 = r'^(\+?\d+(?:\.\d+)?)\s+(.+)$'
        # Pattern 2: "groceries 100" or "salary +100"
        pattern2 = r'^(.+?)\s+(\+?\d+(?:\.\d+)?)$'
        # Pattern 3: "100" (just amount, description = "Transaction")
        pattern3 = r'^(\+?\d+(?:\.\d+)?)$'
        
        match = re.match(pattern1, text.strip())
        if match:
            amount_raw = match.group(1)
            return {
                "amount": float(amount_raw.replace("+", "")),
                "description": match.group(2).strip(),
                "transaction_type": "income" if amount_raw.startswith("+") else "expense"
            }
        
        match = re.match(pattern2, text.strip())
        if match:
            amount_raw = match.group(2)
            return {
                "amount": float(amount_raw.replace("+", "")),
                "description": match.group(1).strip(),
                "transaction_type": "income" if amount_raw.startswith("+") else "expense"
            }
        
        match = re.match(pattern3, text.strip())
        if match:
            amount_raw = match.group(1)
            return {
                "amount": float(amount_raw.replace("+", "")),
                "description": "Транзакция",
                "transaction_type": "income" if amount_raw.startswith("+") else "expense"
            }
        
        return None

    async def _handle_link_command(self, message: TelegramMessageRequest) -> TelegramMessageResponse:
        parts = message.text.strip().split()
        if len(parts) != 2:
            return TelegramMessageResponse(
                success=False,
                message="Используйте: /link КОД. Код можно получить в веб-интерфейсе."
            )

        code = parts[1].strip().upper()
        user = self.user_service.link_telegram_user(
            code=code,
            telegram_user_id=str(message.user_id),
            telegram_username=message.username
        )
        if not user:
            return TelegramMessageResponse(
                success=False,
                message="Код не найден или истек. Получите новый код в веб-интерфейсе."
            )
        return TelegramMessageResponse(
            success=True,
            message="Telegram успешно привязан к вашему аккаунту!"
        )
    
    async def process_webhook(self, update: dict) -> dict:
        """Process incoming webhook from Telegram"""
        try:
            if "message" in update:
                message = update["message"]
                
                # Only process text messages
                if "text" in message:
                    request = TelegramMessageRequest(
                        message_id=message["message_id"],
                        text=message["text"],
                        user_id=message["from"]["id"],
                        username=message["from"].get("username")
                    )
                    
                    response = await self.parse_and_create_transaction(request)
                    return {"ok": True, "response": response.message}
            
            return {"ok": True}
            
        except Exception as e:
            return {"ok": False, "error": str(e)}
