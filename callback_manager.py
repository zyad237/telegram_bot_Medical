"""
Callback data management for 6-level navigation
"""
import re
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class CallbackManager:
    MAX_CALLBACK_LENGTH = 128
    
    @staticmethod
    def sanitize_callback_text(text: str) -> str:
        """Sanitize text for safe callback data"""
        # Replace spaces with underscores and remove special characters
        sanitized = text.replace(' ', '_')
        sanitized = re.sub(r'[^\w\s-]', '', sanitized)
        sanitized = re.sub(r'[-\s]+', '_', sanitized)
        return sanitized
    
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
        """Create subtopic callback data - subtopic is filename"""
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
                # Year selection: y:year_1
                return {"type": "year", "year": callback_data[2:]}
            elif callback_data.startswith("t:"):
                # Term selection: t:year_1:term_1
                parts = callback_data.split(":", 2)
                if len(parts) >= 3:
                    return {"type": "term", "year": parts[1], "term": parts[2]}
            elif callback_data.startswith("b:"):
                # Block selection: b:year_1:term_1:block_1
                parts = callback_data.split(":", 3)
                if len(parts) >= 4:
                    return {"type": "block", "year": parts[1], "term": parts[2], "block": parts[3]}
            elif callback_data.startswith("s:"):
                # Subject selection: s:year_1:term_1:block_1:anatomy
                parts = callback_data.split(":", 4)
                if len(parts) >= 5:
                    return {"type": "subject", "year": parts[1], "term": parts[2], "block": parts[3], "subject": parts[4]}
            elif callback_data.startswith("c:"):
                # Category selection: c:year_1:term_1:block_1:anatomy:general
                parts = callback_data.split(":", 5)
                if len(parts) >= 6:
                    return {"type": "category", "year": parts[1], "term": parts[2], "block": parts[3], "subject": parts[4], "category": parts[5]}
            elif callback_data.startswith("q:"):
                # Subtopic selection: q:year_1:term_1:block_1:anatomy:general:01_Introduction to Anatomy.csv
                parts = callback_data.split(":", 6)
                if len(parts) >= 7:
                    return {"type": "subtopic", "year": parts[1], "term": parts[2], "block": parts[3], "subject": parts[4], "category": parts[5], "subtopic": parts[6]}
        except Exception as e:
            logger.error(f"Error parsing callback data: {e}")
        return None