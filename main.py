#!/usr/bin/env python3
"""
Telegram Quiz Bot - Modular Version
Main entry point that ties all modules together
"""
import logging
from telegram.ext import Application
from telegram.error import TelegramError

from config import TOKEN, CONFIG
from utils import acquire_startup_lock
from database import DatabaseManager
from file_manager import DataManager
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
        
        # Initialize data structure
        DataManager.initialize_data_structure()
        
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
        
        # Log available topics
        from file_manager import FileManager
        topics = FileManager.list_topics()
        if topics:
            logger.info(f"📚 Available topics: {', '.join(topics)}")
            for topic in topics:
                subtopics = FileManager.list_subtopics(topic)
                if subtopics:
                    logger.info(f"   {topic}: {len(subtopics)} subtopics")
        else:
            logger.warning("⚠️ No quiz data found in data folder")
            logger.info("💡 Add CSV files to data/topic_name/ folders and use /refresh")
        
        # Start the bot
        logger.info("🤖 Dynamic Quiz Bot is starting...")
        
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