#!/usr/bin/env python3
"""
Telegram Quiz Bot - Main Entry Point (Railway Compatible)
"""
import logging
import os
from telegram.ext import Application
from telegram.error import TelegramError

from config import TOKEN, CONFIG
from database import DatabaseManager
from file_manager import FileManager
from quiz_manager import QuizManager
from handlers import BotHandlers

# Initialize logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler()  # Railway captures stdout/stderr
    ]
)
logger = logging.getLogger(__name__)

# Railway-compatible startup lock
def acquire_railway_lock():
    """Simple lock mechanism for Railway"""
    lock_file = 'bot.lock'
    if os.path.exists(lock_file):
        logger.warning("⚠️ Lock file exists - another instance might be running")
        return None
    try:
        with open(lock_file, 'w') as f:
            f.write("1")
        logger.info("✅ Railway lock acquired")
        return lock_file
    except Exception as e:
        logger.error(f"❌ Could not acquire lock: {e}")
        return None

async def error_handler(update, context):
    """Global error handler"""
    error = context.error
    logger.error(f"❌ Exception while handling an update: {error}", exc_info=error)
    
    # Ignore common Telegram errors
    if isinstance(error, TelegramError):
        error_msg = str(error).lower()
        if any(msg in error_msg for msg in ["query is too old", "button_data_invalid", "message is not modified"]):
            return
    
    try:
        if update and update.effective_chat:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ An error occurred. Please use /start to begin again."
            )
    except Exception as e:
        logger.error(f"❌ Could not send error message: {e}")

def main():
    """Start the bot with Railway compatibility"""
    
    # Acquire startup lock
    lock_file = acquire_railway_lock()
    
    if not TOKEN:
        logger.error("❌ No bot token provided.")
        return
    
    try:
        # Initialize components
        logger.info("🔄 Initializing components on Railway...")
        
        # Initialize database
        db = DatabaseManager(CONFIG["database_file"])
        
        # Initialize quiz manager
        quiz_manager = QuizManager(db)
        
        # Initialize bot handlers
        bot_handlers = BotHandlers(db, quiz_manager)
        
        # Create application
        application = Application.builder().token(TOKEN).build()
        
        # Register handlers
        bot_handlers.register_handlers(application)
        application.add_error_handler(error_handler)
        
        # Log available years and structure
        years = FileManager.list_years()
        if years:
            logger.info(f"📚 Available years: {', '.join(years)}")
        else:
            logger.warning("⚠️ No academic data found in data folder")
        
        # Start the bot
        logger.info("🤖 Medical Quiz Bot is starting on Railway...")
        
        application.run_polling(
            allowed_updates=['message', 'callback_query', 'poll_answer'],
            drop_pending_updates=True,
            poll_interval=1,
            timeout=30
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")
        print(f"❌ Bot failed to start: {e}")
    
    finally:
        # Release lock on exit
        if lock_file and os.path.exists(lock_file):
            try:
                os.remove(lock_file)
                logger.info("🔓 Railway lock released")
            except Exception as e:
                logger.error(f"❌ Error releasing lock: {e}")

if __name__ == "__main__":
    main()