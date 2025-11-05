"""
Callback data management for 6-level navigation
"""
import re
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class CallbackManager:
    MAX_CALLBACK_LENGTH = 64
    
    @staticmethod
    def sanitize_callback_text(text: str) -> str:
        """Sanitize text for safe callback data"""
        # For numbered filenames, extract just the number for callback
        if text.endswith('.csv') and '_' in text:
            number_part = text.split('_')[0]
            if number_part.isdigit():
                return number_part
        
        # For other text, remove spaces and special chars
        sanitized = text.replace(' ', '')
        sanitized = re.sub(r'[^\w]', '', sanitized)
        sanitized = sanitized.lower()
        return sanitized[:20]
    
    @staticmethod
    def create_year_callback(year: str) -> str:
        """Create year callback data"""
        safe_year = CallbackManager.sanitize_callback_text(year)
        return f"y:{safe_year}"[:CallbackManager.MAX_CALLBACK_LENGTH]
    
    @staticmethod
    def create_term_callback(year: str, term: str) -> str:
        """Create term callback data"""
        safe_year = CallbackManager.sanitize_callback_text(year)
        safe_term = CallbackManager.sanitize_callback_text(term)
        return f"t:{safe_year}:{safe_term}"[:CallbackManager.MAX_CALLBACK_LENGTH]
    
    @staticmethod
    def create_block_callback(year: str, term: str, block: str) -> str:
        """Create block callback data"""
        safe_year = CallbackManager.sanitize_callback_text(year)
        safe_term = CallbackManager.sanitize_callback_text(term)
        safe_block = CallbackManager.sanitize_callback_text(block)
        return f"b:{safe_year}:{safe_term}:{safe_block}"[:CallbackManager.MAX_CALLBACK_LENGTH]
    
    @staticmethod
    def create_subject_callback(year: str, term: str, block: str, subject: str) -> str:
        """Create subject callback data"""
        safe_year = CallbackManager.sanitize_callback_text(year)
        safe_term = CallbackManager.sanitize_callback_text(term)
        safe_block = CallbackManager.sanitize_callback_text(block)
        safe_subject = CallbackManager.sanitize_callback_text(subject)
        return f"s:{safe_year}:{safe_term}:{safe_block}:{safe_subject}"[:CallbackManager.MAX_CALLBACK_LENGTH]
    
    @staticmethod
    def create_category_callback(year: str, term: str, block: str, subject: str, category: str) -> str:
        """Create category callback data"""
        safe_year = CallbackManager.sanitize_callback_text(year)
        safe_term = CallbackManager.sanitize_callback_text(term)
        safe_block = CallbackManager.sanitize_callback_text(block)
        safe_subject = CallbackManager.sanitize_callback_text(subject)
        safe_category = CallbackManager.sanitize_callback_text(category)
        return f"c:{safe_year}:{safe_term}:{safe_block}:{safe_subject}:{safe_category}"[:CallbackManager.MAX_CALLBACK_LENGTH]
    
    @staticmethod
    def create_subtopic_callback(year: str, term: str, block: str, subject: str, category: str, subtopic: str) -> str:
        """Create subtopic callback data - use only number from filename"""
        safe_year = CallbackManager.sanitize_callback_text(year)
        safe_term = CallbackManager.sanitize_callback_text(term)
        safe_block = CallbackManager.sanitize_callback_text(block)
        safe_subject = CallbackManager.sanitize_callback_text(subject)
        safe_category = CallbackManager.sanitize_callback_text(category)
        safe_subtopic = CallbackManager.sanitize_callback_text(subtopic)
        return f"q:{safe_year}:{safe_term}:{safe_block}:{safe_subject}:{safe_category}:{safe_subtopic}"[:CallbackManager.MAX_CALLBACK_LENGTH]
    
    @staticmethod
    def parse_callback_data(callback_data: str) -> Optional[Dict]:
        """Parse callback data safely"""
        try:
            if callback_data == "main_menu":
                return {"type": "main_menu"}
            elif callback_data.startswith("y:"):
                return {"type": "year", "year": callback_data[2:]}
            elif callback_data.startswith("t:"):
                parts = callback_data.split(":", 2)
                if len(parts) >= 3:
                    return {"type": "term", "year": parts[1], "term": parts[2]}
            elif callback_data.startswith("b:"):
                parts = callback_data.split(":", 3)
                if len(parts) >= 4:
                    return {"type": "block", "year": parts[1], "term": parts[2], "block": parts[3]}
            elif callback_data.startswith("s:"):
                parts = callback_data.split(":", 4)
                if len(parts) >= 5:
                    return {"type": "subject", "year": parts[1], "term": parts[2], "block": parts[3], "subject": parts[4]}
            elif callback_data.startswith("c:"):
                parts = callback_data.split(":", 5)
                if len(parts) >= 6:
                    return {"type": "category", "year": parts[1], "term": parts[2], "block": parts[3], "subject": parts[4], "category": parts[5]}
            elif callback_data.startswith("q:"):
                parts = callback_data.split(":", 6)
                if len(parts) >= 7:
                    return {"type": "subtopic", "year": parts[1], "term": parts[2], "block": parts[3], "subject": parts[4], "category": parts[5], "subtopic": parts[6]}
        except Exception as e:
            logger.error(f"Error parsing callback data: {e}")
        return None