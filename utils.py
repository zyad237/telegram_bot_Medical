"""
Utility functions
"""
import os
import fcntl
import logging
import html
import re

logger = logging.getLogger(__name__)

def acquire_startup_lock():
    """Prevent multiple instances from running"""
    lock_file = os.path.join(os.path.dirname(__file__), 'bot.lock')
    
    try:
        lock_fd = open(lock_file, 'w')
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        logger.info("✅ Startup lock acquired")
        return lock_fd
    except (IOError, OSError):
        logger.error("❌ Another bot instance is already running!")
        exit(1)

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