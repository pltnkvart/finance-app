import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.schemas.telegram import TelegramMessageRequest
from app.domain.services.telegram_service import TelegramService

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class FinTrackBot:
    def __init__(self):
        self.application = Application.builder().token(
            settings.TELEGRAM_BOT_TOKEN
        ).build()
        
        # Add handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("stats", self.stats_command))
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )
        
        logger.info("FinTrack Telegram Bot initialized")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = (
            "Welcome to FinTrack Bot! 🎉\n\n"
            "I help you track your expenses quickly and easily.\n\n"
            "Just send me a message with the amount and description:\n"
            "• '100 groceries'\n"
            "• '50.5 coffee'\n"
            "• 'lunch 25'\n\n"
            "I'll automatically categorize your transactions and you can view them in the dashboard.\n\n"
            "Use /help for more information."
        )
        await update.message.reply_text(welcome_message)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_message = (
            "📝 How to use FinTrack Bot:\n\n"
            "Send a message with:\n"
            "1. Amount (required)\n"
            "2. Description (optional)\n\n"
            "Examples:\n"
            "• '100 groceries at supermarket'\n"
            "• '25.50 uber ride'\n"
            "• 'coffee 5'\n"
            "• '100' (will be labeled as 'Transaction')\n\n"
            "Commands:\n"
            "/start - Start the bot\n"
            "/help - Show this help message\n"
            "/stats - View your transaction statistics\n\n"
            "The bot will automatically categorize your transactions based on the description!"
        )
        await update.message.reply_text(help_message)
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command"""
        db = SessionLocal()
        try:
            from app.domain.services.statistics_service import StatisticsService
            service = StatisticsService(db)
            summary = service.get_summary()
            
            stats_message = (
                f"📊 Your Statistics:\n\n"
                f"Total Transactions: {summary['transaction_count']}\n"
                f"Total Amount: ${summary['total_amount']:.2f}\n\n"
                f"View detailed analytics in the dashboard!"
            )
            await update.message.reply_text(stats_message)
        finally:
            db.close()
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming text messages"""
        db = SessionLocal()
        try:
            # Create request object
            request = TelegramMessageRequest(
                message_id=update.message.message_id,
                text=update.message.text,
                user_id=update.message.from_user.id,
                username=update.message.from_user.username
            )
            
            # Process message
            service = TelegramService(db)
            response = await service.parse_and_create_transaction(request)
            
            if response.success:
                # Get category name
                from app.models.transaction import Transaction
                transaction = db.query(Transaction).filter(
                    Transaction.id == response.transaction_id
                ).first()
                
                category_name = transaction.category.name if transaction and transaction.category else "Uncategorized"
                
                reply_message = (
                    f"✅ Transaction saved!\n\n"
                    f"Amount: ${response.parsed_data['amount']:.2f}\n"
                    f"Description: {response.parsed_data['description']}\n"
                    f"Category: {category_name}"
                )
                await update.message.reply_text(reply_message)
            else:
                await update.message.reply_text(
                    f"❌ {response.message}\n\n"
                    f"Try formats like:\n"
                    f"• '100 groceries'\n"
                    f"• '50.5 coffee'"
                )
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await update.message.reply_text(
                "❌ Sorry, there was an error processing your transaction. Please try again."
            )
        finally:
            db.close()
    
    def run(self):
        """Start the bot"""
        logger.info("Starting FinTrack Telegram Bot...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)
    
    async def start_webhook(self, webhook_url: str):
        """Start bot with webhook"""
        await self.application.bot.set_webhook(url=webhook_url)
        logger.info(f"Webhook set to: {webhook_url}")


def create_bot() -> FinTrackBot:
    """Factory function to create bot instance"""
    return FinTrackBot()
