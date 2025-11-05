#!/usr/bin/env python3
"""
Telegram Quiz Bot - Main Entry Point
"""
import logging
from telegram.ext import Application
from telegram.error import TelegramError

from config import TOKEN, CONFIG
from utils import acquire_startup_lock
from database import DatabaseManager
from file_manager import FileManager
from quiz_manager import QuizManager
from handlers import BotHandlers

# Initialize logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('quiz_bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

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
    """Start the bot with all modules integrated"""
    
    # Acquire startup lock to prevent multiple instances
    lock_fd = acquire_startup_lock()
    lock_file = 'bot.lock'
    
    if not TOKEN:
        logger.error("❌ No bot token provided.")
        return
    
    try:
        # Initialize components
        logger.info("🔄 Initializing components...")
        
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
            for year in years:
                terms = FileManager.list_terms(year)
                if terms:
                    logger.info(f"   {year}: {len(terms)} terms")
                    for term in terms:
                        blocks = FileManager.list_blocks(year, term)
                        if blocks:
                            logger.info(f"     {term}: {len(blocks)} blocks")
                            for block in blocks:
                                subjects = FileManager.list_subjects(year, term, block)
                                if subjects:
                                    logger.info(f"       {block}: {len(subjects)} subjects")
                                    for subject in subjects:
                                        categories = FileManager.list_categories(year, term, block, subject)
                                        if categories:
                                            logger.info(f"         {subject}: {len(categories)} categories")
        else:
            logger.warning("⚠️ No academic data found in data folder")
            logger.info("💡 Please check your data directory structure:")
            logger.info("   data/year_1/term_1/block_1/subject/category/")
        
        # Start the bot
        logger.info("🤖 Medical Quiz Bot is starting...")
        
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
        if lock_fd:
            try:
                import fcntl
                import os
                fcntl.flock(lock_fd, fcntl.LOCK_UN)
                lock_fd.close()
                if os.path.exists(lock_file):
                    os.remove(lock_file)
                logger.info("🔓 Startup lock released")
            except Exception as e:
                logger.error(f"❌ Error releasing lock: {e}")

if __name__ == "__main__":
    main()