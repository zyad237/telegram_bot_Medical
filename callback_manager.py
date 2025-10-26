"""
Callback data management
"""
import re
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class CallbackManager:
    """Manage callback data to work with actual filenames"""
    
    MAX_CALLBACK_LENGTH = 128
    
    @staticmethod
    def sanitize_callback_text(text: str) -> str:
        """Sanitize text for safe callback data"""
        sanitized = re.sub(r'[^\w\s-]', '', text)
        sanitized = re.sub(r'[-\s]+', '_', sanitized)
        return sanitized.lower()  # No truncation - uses full filename
    
    @staticmethod
    def create_topic_callback(topic: str) -> str:
        """Create safe topic callback data"""
        safe_topic = CallbackManager.sanitize_callback_text(topic)
        return f"t:{safe_topic}"[:CallbackManager.MAX_CALLBACK_LENGTH]
    
    @staticmethod
    def create_subtopic_callback(topic: str, subtopic: str) -> str:
        """Create safe subtopic callback data using actual subtopic name"""
        safe_topic = CallbackManager.sanitize_callback_text(topic)
        safe_subtopic = CallbackManager.sanitize_callback_text(subtopic)
        return f"s:{safe_topic}:{safe_subtopic}"[:CallbackManager.MAX_CALLBACK_LENGTH]
    
    @staticmethod
    def parse_callback_data(callback_data: str) -> Optional[Dict]:
        """Parse callback data safely"""
        try:
            if callback_data == "main_menu":
                return {"type": "main_menu"}
            elif callback_data == "refresh_topics":
                return {"type": "refresh_topics"}
            elif callback_data.startswith("t:"):
                return {"type": "topic", "topic": callback_data[2:]}
            elif callback_data.startswith("s:"):
                parts = callback_data.split(":", 2)
                if len(parts) >= 3:
                    return {"type": "subtopic", "topic": parts[1], "subtopic": parts[2]}
        except Exception as e:
            logger.error(f"Error parsing callback data: {e}")
        return None