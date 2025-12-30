"""
Run the Telegram bot in polling mode
This script should be run separately from the FastAPI server
"""
import asyncio
from app.bot.telegram_bot import create_bot


def main():
    """Main entry point for the bot"""
    bot = create_bot()
    bot.run()


if __name__ == "__main__":
    main()
