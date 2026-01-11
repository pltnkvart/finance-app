import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CallbackQueryHandler,
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
from app.domain.services.user_service import UserService

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
        self.application.add_handler(CommandHandler("link", self.link_command))
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )
        self.application.add_handler(
            CallbackQueryHandler(self.handle_account_selection, pattern="^account:")
        )
        self.application.add_handler(
            CallbackQueryHandler(self.handle_category_parent_selection, pattern="^cat-parent:")
        )
        self.application.add_handler(
            CallbackQueryHandler(self.handle_category_selection, pattern="^cat:")
        )
        self.application.add_handler(
            CallbackQueryHandler(self.handle_category_none, pattern="^cat-none:")
        )
        self.application.add_handler(
            CallbackQueryHandler(self.handle_category_back, pattern="^cat-back:")
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
            "Для доходов используйте плюс:\n"
            "• '+50000 зарплата'\n\n"
            "После создания транзакции выберите счет и категорию через кнопки.\n\n"
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
            "Доходы:\n"
            "• '+50000 зарплата'\n"
            "• '+1200 проценты по вкладу'\n\n"
            "Команды:\n"
            "/start - Запустить бота\n"
            "/help - Показать это справочное сообщение\n"
            "/stats - Посмотреть статистику транзакций\n\n"
            "/link КОД - Привязать Telegram к аккаунту\n\n"
            "После создания транзакции выберите счет и категорию через кнопки."
        )
        await update.message.reply_text(help_message)

    async def link_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /link command"""
        db = SessionLocal()
        try:
            if not context.args or len(context.args) != 1:
                await update.message.reply_text(
                    "Используйте: /link КОД. Код можно получить в веб-интерфейсе."
                )
                return

            code = context.args[0].strip().upper()
            service = UserService(db)
            user = service.link_telegram_user(
                code=code,
                telegram_user_id=str(update.message.from_user.id),
                telegram_username=update.message.from_user.username
            )
            if not user:
                await update.message.reply_text("Код не найден или истек. Получите новый код в веб-интерфейсе.")
                return

            await update.message.reply_text("Telegram успешно привязан к вашему аккаунту!")
        finally:
            db.close()
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command"""
        db = SessionLocal()
        try:
            from app.domain.services.statistics_service import StatisticsService
            from app.models.user import User
            user = db.query(User).filter(User.telegram_user_id == str(update.message.from_user.id)).first()
            if not user:
                await update.message.reply_text("Telegram не привязан. Получите код в веб-интерфейсе и отправьте: /link КОД.")
                return
            service = StatisticsService(db)
            summary = service.get_summary(user.id)
            
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
                from app.models.account import Account
                user_service = UserService(db)
                user = user_service.get_by_telegram_id(str(update.message.from_user.id))
                if not user:
                    await update.message.reply_text(
                        "Ваш Telegram не привязан. Получите код в веб-интерфейсе и отправьте: /link КОД"
                    )
                    return

                accounts = db.query(Account).filter(Account.user_id == user.id).order_by(Account.name.asc()).all()
                transaction_type = response.parsed_data.get("transaction_type", "expense")
                account_prompt = "Выберите счет зачисления:" if transaction_type == "income" else "Выберите счет списания:"

                reply_message = (
                    f"✅ Транзакция сохранена!\n\n"
                    f"Сумма: {response.parsed_data['amount']:.2f} ₽\n"
                    f"Описание: {response.parsed_data['description']}\n"
                    f"{account_prompt}"
                )
                if not accounts:
                    await update.message.reply_text(
                        "⚠️ Нет доступных счетов. Сначала создайте счет в интерфейсе."
                    )
                else:
                    await update.message.reply_text(
                        reply_message,
                        reply_markup=self._build_accounts_keyboard(accounts, response.transaction_id)
                    )
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

    async def handle_account_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        parts = query.data.split(":")
        if len(parts) != 3:
            await query.edit_message_text("❌ Не удалось определить счет.")
            return

        transaction_id = int(parts[1])
        account_id = int(parts[2])

        db = SessionLocal()
        try:
            from app.domain.services.transaction_service import TransactionService
            from app.schemas.transaction import TransactionUpdate
            from app.models.account import Account
            from app.models.transaction import Transaction, TransactionType
            from app.models.user import User

            service = TransactionService(db)
            user = db.query(User).filter(User.telegram_user_id == str(query.from_user.id)).first()
            if not user:
                await query.edit_message_text("❌ Telegram не привязан. Используйте /link КОД.")
                return

            transaction = service.update_transaction(
                transaction_id,
                TransactionUpdate(account_id=account_id),
                user.id
            )

            account = db.query(Account).filter(Account.id == account_id, Account.user_id == user.id).first()
            account_name = account.name if account else "Неизвестный счет"

            if not transaction:
                await query.edit_message_text("❌ Транзакция не найдена.")
                return

            await query.edit_message_text(f"✅ Счет выбран: {account_name}")

            transaction_type = (
                transaction.transaction_type
                if hasattr(transaction, "transaction_type")
                else db.query(Transaction).filter(Transaction.id == transaction_id).first().transaction_type
            )

            if transaction_type == TransactionType.INCOME:
                await query.message.reply_text(
                    self._build_confirmation_message(
                        transaction=transaction,
                        account_name=account_name,
                        category_name=None
                    )
                )
                return

            parent_keyboard = self._build_parent_categories_keyboard(db, transaction_id)
            if not parent_keyboard.inline_keyboard:
                await query.message.reply_text("⚠️ Категорий пока нет. Создайте их в интерфейсе.")
                return

            await query.message.reply_text(
                "Теперь выберите категорию:",
                reply_markup=parent_keyboard
            )
        finally:
            db.close()

    async def handle_category_parent_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        parts = query.data.split(":")
        if len(parts) != 3:
            await query.edit_message_text("❌ Не удалось определить категорию.")
            return

        transaction_id = int(parts[1])
        category_id = int(parts[2])

        db = SessionLocal()
        try:
            from app.models.category import Category

            children = db.query(Category).filter(Category.parent_id == category_id).all()
            if not children:
                await self._set_transaction_category(db, query, transaction_id, category_id)
                return

            await query.edit_message_text(
                "Выберите подкатегорию:",
                reply_markup=self._build_child_categories_keyboard(
                    transaction_id,
                    children
                )
            )
        finally:
            db.close()

    async def handle_category_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        parts = query.data.split(":")
        if len(parts) != 3:
            await query.edit_message_text("❌ Не удалось определить категорию.")
            return

        transaction_id = int(parts[1])
        category_id = int(parts[2])

        db = SessionLocal()
        try:
            await self._set_transaction_category(db, query, transaction_id, category_id)
        finally:
            db.close()

    async def handle_category_none(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        parts = query.data.split(":")
        if len(parts) != 2:
            await query.edit_message_text("❌ Не удалось определить транзакцию.")
            return

        transaction_id = int(parts[1])

        db = SessionLocal()
        try:
            from app.domain.services.transaction_service import TransactionService
            from app.schemas.transaction import TransactionUpdate
            from app.models.account import Account
            from app.models.user import User

            service = TransactionService(db)
            user = db.query(User).filter(User.telegram_user_id == str(query.from_user.id)).first()
            if not user:
                await query.edit_message_text("❌ Telegram не привязан. Используйте /link КОД.")
                return
            transaction = service.update_transaction(
                transaction_id,
                TransactionUpdate(category_id=None),
                user.id
            )

            if not transaction:
                await query.edit_message_text("❌ Транзакция не найдена.")
                return

            account_name = transaction.account.name if transaction.account else None
            await query.edit_message_text("✅ Категория не указана.")
            await query.message.reply_text(
                self._build_confirmation_message(
                    transaction=transaction,
                    account_name=account_name,
                    category_name=None
                )
            )
        finally:
            db.close()

    async def handle_category_back(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        parts = query.data.split(":")
        if len(parts) != 2:
            await query.edit_message_text("❌ Не удалось определить транзакцию.")
            return

        transaction_id = int(parts[1])

        db = SessionLocal()
        try:
            await query.edit_message_text(
                "Выберите категорию:",
                reply_markup=self._build_parent_categories_keyboard(db, transaction_id)
            )
        finally:
            db.close()

    def _build_accounts_keyboard(self, accounts: list, transaction_id: int) -> InlineKeyboardMarkup:
        buttons = [
            InlineKeyboardButton(
                account.name,
                callback_data=f"account:{transaction_id}:{account.id}"
            )
            for account in accounts
        ]

        return InlineKeyboardMarkup(self._chunk_buttons(buttons))

    def _build_parent_categories_keyboard(self, db: Session, transaction_id: int) -> InlineKeyboardMarkup:
        from app.models.category import Category

        categories = db.query(Category).filter(Category.parent_id.is_(None)).order_by(Category.name.asc()).all()
        buttons = [
            InlineKeyboardButton(
                category.name,
                callback_data=f"cat-parent:{transaction_id}:{category.id}"
            )
            for category in categories
        ]
        buttons.append(
            InlineKeyboardButton("Без категории", callback_data=f"cat-none:{transaction_id}")
        )

        return InlineKeyboardMarkup(self._chunk_buttons(buttons))

    def _build_child_categories_keyboard(self, transaction_id: int, categories: list) -> InlineKeyboardMarkup:
        buttons = [
            InlineKeyboardButton(
                category.name,
                callback_data=f"cat:{transaction_id}:{category.id}"
            )
            for category in categories
        ]
        buttons.append(
            InlineKeyboardButton("Назад", callback_data=f"cat-back:{transaction_id}")
        )

        return InlineKeyboardMarkup(self._chunk_buttons(buttons))

    def _chunk_buttons(self, buttons: list[InlineKeyboardButton], size: int = 2) -> list[list[InlineKeyboardButton]]:
        return [buttons[i:i + size] for i in range(0, len(buttons), size)]

    async def _set_transaction_category(
        self,
        db: Session,
        query,
        transaction_id: int,
        category_id: int
    ) -> None:
        from app.domain.services.transaction_service import TransactionService
        from app.schemas.transaction import TransactionUpdate
        from app.models.category import Category
        from app.models.user import User

        service = TransactionService(db)
        user = db.query(User).filter(User.telegram_user_id == str(query.from_user.id)).first()
        if not user:
            await query.edit_message_text("❌ Telegram не привязан. Используйте /link КОД.")
            return
        transaction = service.update_transaction(
            transaction_id,
            TransactionUpdate(category_id=category_id),
            user.id
        )

        category = db.query(Category).filter(Category.id == category_id).first()
        category_name = category.name if category else "Неизвестная категория"

        if not transaction:
            await query.edit_message_text("❌ Транзакция не найдена.")
            return

        await query.edit_message_text(f"✅ Категория выбрана: {category_name}")
        await query.message.reply_text(
            self._build_confirmation_message(
                transaction=transaction,
                account_name=transaction.account.name if transaction.account else None,
                category_name=category_name
            )
        )

    def _build_confirmation_message(self, transaction, account_name: str | None, category_name: str | None) -> str:
        transaction_type = getattr(transaction, "transaction_type", None)
        type_label = "Доход" if transaction_type and transaction_type.value == "income" else "Расход"
        account_line = f"Счет: {account_name}" if account_name else "Счет: не указан"
        category_line = f"Категория: {category_name}" if category_name else "Категория: не указана"

        return (
            "✅ Записано:\n\n"
            f"Тип: {type_label}\n"
            f"Сумма: {float(transaction.amount):.2f} ₽\n"
            f"Описание: {transaction.description}\n"
            f"{account_line}\n"
            f"{category_line}"
        )
    
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
