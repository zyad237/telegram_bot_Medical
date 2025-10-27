"""
File and data management with nested structure
"""
import os
import csv
import logging
from typing import List, Dict, Tuple
from functools import lru_cache

from config import CONFIG, TOPIC_DISPLAY_NAMES, NESTED_STRUCTURE
from utils import validate_topic_name, validate_subtopic_name, sanitize_text

logger = logging.getLogger(__name__)

class FileManager:
    @staticmethod
    @lru_cache(maxsize=32)
    def list_topics() -> List[str]:
        """Get list of available topics from data directory"""
        data_dir = CONFIG["data_dir"]
        if not os.path.exists(data_dir):
            return []
        
        topics = [d for d in os.listdir(data_dir) 
                 if os.path.isdir(os.path.join(data_dir, d)) 
                 and not d.startswith('.')
                 and d in TOPIC_DISPLAY_NAMES]
        return sorted(topics)
    
    @staticmethod
    def get_topic_display_name(topic: str) -> str:
        """Get manual display name for topic"""
        return TOPIC_DISPLAY_NAMES.get(topic, topic.title())
    
    @staticmethod
    @lru_cache(maxsize=128)
    def list_categories(topic: str) -> List[str]:
        """Get list of available categories for a topic"""
        if not validate_topic_name(topic) or topic not in NESTED_STRUCTURE:
            return []
            
        topic_path = os.path.join(CONFIG["data_dir"], topic)
        if not os.path.exists(topic_path):
            return []
        
        # Only return categories that exist in both directory and nested structure
        categories = []
        for item in os.listdir(topic_path):
            item_path = os.path.join(topic_path, item)
            if os.path.isdir(item_path) and not item.startswith('.'):
                if topic in NESTED_STRUCTURE and item in NESTED_STRUCTURE[topic]:
                    categories.append(item)
        
        return sorted(categories)
    
    @staticmethod
    def get_category_display_name(topic: str, category: str) -> str:
        """Get display name for category"""
        if (topic in NESTED_STRUCTURE and 
            category in NESTED_STRUCTURE[topic]):
            return NESTED_STRUCTURE[topic][category]["display_name"]
        return category.title()
    
    @staticmethod
    @lru_cache(maxsize=256)
    def list_subtopics(topic: str, category: str) -> List[str]:
        """Get list of available subtopics for a category"""
        if (not validate_topic_name(topic) or 
            topic not in NESTED_STRUCTURE or 
            category not in NESTED_STRUCTURE[topic]):
            return []
            
        category_path = os.path.join(CONFIG["data_dir"], topic, category)
        if not os.path.exists(category_path):
            return []
        
        # Only return subtopics that exist in both directory and nested structure
        subtopics = []
        for file in os.listdir(category_path):
            if file.endswith('.csv') and not file.startswith('.'):
                subtopic_name = file[:-4]  # Remove .csv extension
                if (validate_subtopic_name(subtopic_name) and 
                    "subtopics" in NESTED_STRUCTURE[topic][category] and
                    subtopic_name in NESTED_STRUCTURE[topic][category]["subtopics"]):
                    subtopics.append(subtopic_name)
        
        return sorted(subtopics)
    
    @staticmethod
    def get_subtopic_display_name(topic: str, category: str, subtopic: str) -> str:
        """Get display name for subtopic"""
        if (topic in NESTED_STRUCTURE and 
            category in NESTED_STRUCTURE[topic] and
            "subtopics" in NESTED_STRUCTURE[topic][category] and
            subtopic in NESTED_STRUCTURE[topic][category]["subtopics"]):
            return NESTED_STRUCTURE[topic][category]["subtopics"][subtopic]
        return subtopic.title()
    
    @staticmethod
    def load_questions(topic: str, category: str, subtopic: str) -> List[Dict]:
        """Load questions from CSV file in nested directory structure"""
        # Security validation
        if (not validate_topic_name(topic) or 
            not validate_subtopic_name(category) or 
            not validate_subtopic_name(subtopic)):
            logger.error(f"❌ Invalid names: {topic}/{category}/{subtopic}")
            return []
            
        # Check if this topic/category/subtopic exists in nested structure
        if (topic not in NESTED_STRUCTURE or 
            category not in NESTED_STRUCTURE[topic] or
            "subtopics" not in NESTED_STRUCTURE[topic][category] or
            subtopic not in NESTED_STRUCTURE[topic][category]["subtopics"]):
            logger.error(f"❌ Not in nested structure: {topic}/{category}/{subtopic}")
            return []
        
        # Construct file path from nested directory structure
        filename = f"{subtopic}.csv"
        file_path = os.path.join(CONFIG["data_dir"], topic, category, filename)
        
        logger.info(f"📁 Loading questions from: {file_path}")
        
        if not os.path.exists(file_path):
            logger.error(f"❌ Question file not found: {file_path}")
            return []
        
        questions = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                row_count = 0
                valid_questions = 0
                
                for i, row in enumerate(reader, 1):
                    row_count += 1
                    
                    # Skip empty rows, comments, and rows with insufficient data
                    if not row or not any(row) or row[0].startswith('#') or len(row) < 6:
                        continue
                    
                    # Clean and validate data
                    cleaned_row = [x.strip() for x in row[:6] if x.strip()]
                    if len(cleaned_row) < 6:
                        continue
                    
                    question, opt_a, opt_b, opt_c, opt_d, correct = cleaned_row
                    correct = correct.upper()
                    
                    # Validate correct answer format
                    if correct not in ['A', 'B', 'C', 'D']:
                        logger.warning(f"⚠️ Invalid correct answer in row {i}: '{correct}'")
                        continue
                    
                    # Sanitize all text
                    question = sanitize_text(question)
                    opt_a = sanitize_text(opt_a)
                    opt_b = sanitize_text(opt_b)
                    opt_c = sanitize_text(opt_c)
                    opt_d = sanitize_text(opt_d)
                    
                    questions.append({
                        "question": question,
                        "options": [opt_a, opt_b, opt_c, opt_d],
                        "correct": correct,
                        "correct_index": ord(correct) - ord('A')
                    })
                    valid_questions += 1
            
            logger.info(f"✅ Loaded {valid_questions} valid questions from {row_count} rows")
            
            if valid_questions == 0:
                logger.warning(f"⚠️ No valid questions found in {file_path}")
                
        except Exception as e:
            logger.error(f"❌ Error loading questions from {file_path}: {e}")
        
        return questions