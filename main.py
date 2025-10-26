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
        
        # Initialize database - make sure CONFIG has 'database_file' key
        logger.info(f"📁 Database file: {CONFIG.get('database_file', 'NOT FOUND')}")
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
        topics = FileManager.list_topics()
        if topics:
            logger.info(f"📚 Available topics: {', '.join(topics)}")
            for topic in topics:
                subtopics = FileManager.list_subtopics(topic)
                if subtopics:
                    logger.info(f"   {topic}: {len(subtopics)} subtopics")
        else:
            logger.warning("⚠️ No quiz data found in data folder")
            logger.info("💡 Please check:")
            logger.info("   - Data directory exists with topic folders")
            logger.info("   - CSV files are in correct format") 
            logger.info("   - Topics are defined in config.py")
        
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