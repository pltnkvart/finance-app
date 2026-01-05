from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import re
from datetime import datetime

from app.schemas.telegram import TelegramMessageRequest, TelegramMessageResponse
from app.schemas.transaction import TransactionCreate
from app.domain.services.transaction_service import TransactionService
from app.domain.services.categorization_service import CategorizationService


class TelegramService:
    def __init__(self, db: Session):
        self.db = db
        self.transaction_service = TransactionService(db)
        self.categorization_service = CategorizationService(db)
    
    async def parse_and_create_transaction(
        self, 
        message: TelegramMessageRequest
    ) -> TelegramMessageResponse:
        """Parse Telegram message and create transaction"""
        try:
            # Parse the message text
            parsed_data = self._parse_message(message.text)
            
            if not parsed_data:
                return TelegramMessageResponse(
                    success=False,
                    message="Не удалось распознать транзакцию. Используйте формат: '100 продукты' или '50.5 кофе'"
                )
            
            # Predict category
            predicted_category = self.categorization_service.predict_category(
                parsed_data["description"]
            )
            
            # Create transaction
            transaction_data = TransactionCreate(
                amount=parsed_data["amount"],
                description=parsed_data["description"],
                transaction_date=datetime.now(),
                category_id=predicted_category,
                telegram_message_id=message.message_id,
                raw_text=message.text
            )
            
            transaction = self.transaction_service.create_transaction(transaction_data)
            
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
        # Pattern 1: "100 groceries" or "50.5 coffee"
        pattern1 = r'^(\d+(?:\.\d+)?)\s+(.+)$'
        # Pattern 2: "groceries 100" or "coffee 50.5"
        pattern2 = r'^(.+?)\s+(\d+(?:\.\d+)?)$'
        # Pattern 3: "100" (just amount, description = "Transaction")
        pattern3 = r'^(\d+(?:\.\d+)?)$'
        
        match = re.match(pattern1, text.strip())
        if match:
            return {
                "amount": float(match.group(1)),
                "description": match.group(2).strip()
            }
        
        match = re.match(pattern2, text.strip())
        if match:
            return {
                "amount": float(match.group(2)),
                "description": match.group(1).strip()
            }
        
        match = re.match(pattern3, text.strip())
        if match:
            return {
                "amount": float(match.group(1)),
                "description": "Транзакция"
            }
        
        return None
    
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
