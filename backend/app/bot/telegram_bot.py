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
            "Добро пожаловать в FinTrack Bot! 🎉\n\n"
            "Я помогу вам быстро и легко отслеживать ваши расходы.\n\n"
            "Просто отправьте мне сообщение с суммой и описанием:\n"
            "• '100 продукты'\n"
            "• '50.5 кофе'\n"
            "• 'обед 25'\n\n"
            "Я автоматически категоризирую ваши транзакции, и вы сможете просматривать их в дашборде.\n\n"
            "Используйте /help для получения дополнительной информации."
        )
        await update.message.reply_text(welcome_message)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_message = (
            "📝 Как использовать FinTrack Bot:\n\n"
            "Отправьте сообщение с:\n"
            "1. Сумма (обязательно)\n"
            "2. Описание (опционально)\n\n"
            "Примеры:\n"
            "• '100 продукты в супермаркете'\n"
            "• '25.50 такси убер'\n"
            "• 'кофе 5'\n"
            "• '100' (будет помечено как 'Транзакция')\n\n"
            "Команды:\n"
            "/start - Запустить бота\n"
            "/help - Показать это справочное сообщение\n"
            "/stats - Посмотреть статистику транзакций\n\n"
            "Бот автоматически категоризирует ваши транзакции на основе описания!"
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
                f"📊 Ваша статистика:\n\n"
                f"Всего транзакций: {summary['transaction_count']}\n"
                f"Общая сумма: {summary['total_amount']:.2f} ₽\n\n"
                f"Просмотрите подробную аналитику в дашборде!"
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
                    f"✅ Транзакция сохранена!\n\n"
                    f"Сумма: {response.parsed_data['amount']:.2f} ₽\n"
                    f"Описание: {response.parsed_data['description']}\n"
                    f"Категория: {category_name}"
                )
                await update.message.reply_text(reply_message)
            else:
                await update.message.reply_text(
                    f"❌ {response.message}\n\n"
                    f"Попробуйте форматы:\n"
                    f"• '100 продукты'\n"
                    f"• '50.5 кофе'"
                )
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await update.message.reply_text(
                "❌ Извините, произошла ошибка при обработке вашей транзакции. Пожалуйста, попробуйте снова."
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
