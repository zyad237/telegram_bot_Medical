"""
Windows-compatible utils without fcntl dependency
"""
import os
import logging
import html
import re

logger = logging.getLogger(__name__)

def acquire_startup_lock():
    """
    Windows-compatible startup lock using file creation
    """
    lock_file = os.path.join(os.path.dirname(__file__), 'bot.lock')
    
    try:
        # Try to create the lock file exclusively
        if os.path.exists(lock_file):
            # Check if lock file is stale (older than 5 minutes)
            import time
            file_age = time.time() - os.path.getmtime(lock_file)
            if file_age > 300:  # 5 minutes
                logger.warning("⚠️ Removing stale lock file")
                os.remove(lock_file)
            else:
                logger.error("❌ Another bot instance might be running!")
                return None
        
        # Create lock file
        with open(lock_file, 'w') as f:
            f.write(str(os.getpid()))
        
        logger.info("✅ Startup lock acquired (Windows compatible)")
        return lock_file
        
    except Exception as e:
        logger.error(f"❌ Could not acquire lock: {e}")
        return None

def sanitize_text(text: str) -> str:
    """Sanitize text to prevent Markdown parsing errors"""
    if not text:
        return ""
    
    text = html.escape(text)
    markdown_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    
    for char in markdown_chars:
        text = text.replace(char, f'\\{char}')
    
    text = re.sub(r'\\+', r'\\', text)
    return text

def validate_topic_name(topic: str) -> bool:
    """Prevent path traversal attacks"""
    if not topic or len(topic) > 100:
        return False
    if any(char in topic for char in ['/', '\\', '..', '~']):
        return False
    return re.match(r'^[\w\s-]+$', topic) is not None

def validate_subtopic_name(subtopic: str) -> bool:
    """Validate subtopic name"""
    if not subtopic or len(subtopic) > 100:
        return False
    if any(char in subtopic for char in ['/', '\\', '..']):
        return False
    return re.match(r'^[\w\s-]+$', subtopic) is not None