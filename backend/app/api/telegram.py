from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.schemas.telegram import TelegramMessageRequest, TelegramMessageResponse
from app.domain.services.telegram_service import TelegramService

router = APIRouter()


@router.post("/parse", response_model=TelegramMessageResponse)
async def parse_telegram_message(
    message: TelegramMessageRequest,
    db: Session = Depends(get_db)
):
    """Parse a Telegram message and create a transaction"""
    service = TelegramService(db)
    return await service.parse_and_create_transaction(message)


@router.post("/webhook")
async def telegram_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Webhook endpoint for Telegram bot
    
    To set up webhook, send a POST request to:
    https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=<YOUR_WEBHOOK_URL>
    
    Example:
    https://api.telegram.org/bot123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11/setWebhook?url=https://yourdomain.com/api/telegram/webhook
    """
    try:
        update = await request.json()
        service = TelegramService(db)
        result = await service.process_webhook(update)
        return result
    except Exception as e:
        return {"ok": False, "error": str(e)}


@router.get("/webhook-info")
async def get_webhook_info():
    """
    Get information about setting up the webhook
    """
    return {
        "message": "To set up Telegram webhook:",
        "steps": [
            "1. Get your bot token from @BotFather",
            "2. Deploy your FastAPI server with a public URL (HTTPS required)",
            "3. Send POST request to: https://api.telegram.org/bot<TOKEN>/setWebhook",
            "4. Include parameter: url=<YOUR_DOMAIN>/api/telegram/webhook",
            "5. Alternatively, run the bot in polling mode using run_bot.py"
        ],
        "polling_mode": "Run 'python run_bot.py' for local development",
        "webhook_endpoint": "/api/telegram/webhook"
    }
