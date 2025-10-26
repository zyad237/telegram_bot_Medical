"""
File and data management with manual display names
"""
import os
import csv
import logging
from typing import List, Dict
from functools import lru_cache

from config import CONFIG, TOPIC_DISPLAY_NAMES, SUBPROJECT_DISPLAY_NAMES
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
        
        # Only return topics that exist in both directory and display names
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
    def list_subtopics(topic: str) -> List[str]:
        """Get list of available subtopics for a topic"""
        if not validate_topic_name(topic) or topic not in TOPIC_DISPLAY_NAMES:
            return []
            
        topic_path = os.path.join(CONFIG["data_dir"], topic)
        if not os.path.exists(topic_path):
            return []
        
        # Only return subtopics that exist in both directory and display names
        subtopics = []
        for file in os.listdir(topic_path):
            if file.endswith('.csv') and not file.startswith('.'):
                subtopic_name = file[:-4]  # Remove .csv extension
                if (validate_subtopic_name(subtopic_name) and 
                    topic in SUBPROJECT_DISPLAY_NAMES and 
                    subtopic_name in SUBPROJECT_DISPLAY_NAMES[topic]):
                    subtopics.append(subtopic_name)
        
        return sorted(subtopics)
    
    @staticmethod
    def get_subtopic_display_name(topic: str, subtopic: str) -> str:
        """Get manual display name for subtopic"""
        if (topic in SUBPROJECT_DISPLAY_NAMES and 
            subtopic in SUBPROJECT_DISPLAY_NAMES[topic]):
            return SUBPROJECT_DISPLAY_NAMES[topic][subtopic]
        return subtopic.title()
    
    @staticmethod
    def validate_csv_format(file_path: str) -> bool:
        """Validate CSV file has correct format"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for i, row in enumerate(reader, 1):
                    if not row or row[0].startswith('#'):
                        continue
                    if len(row) < 6:
                        return False
                    if row[5].upper() not in ['A', 'B', 'C', 'D']:
                        return False
            return True
        except Exception as e:
            logger.error(f"❌ CSV validation failed: {e}")
            return False
    
    @staticmethod
    def load_questions(topic: str, subtopic: str) -> List[Dict]:
        """Load questions from CSV file in data directory"""
            # Debug: Print what we're looking for
        print(f"🔍 Looking for: topic='{topic}', subtopic='{subtopic}'")
    
    # Debug: List all available topics and subtopics
        print(f"📁 Available topics: {FileManager.list_topics()}")
        if topic in FileManager.list_topics():
            print(f"📄 Available subtopics for {topic}: {FileManager.list_subtopics(topic)}")
        # Security validation
        if not validate_topic_name(topic) or not validate_subtopic_name(subtopic):
            logger.error(f"❌ Invalid topic or subtopic name: {topic}/{subtopic}")
            return []
            
        # Check if this topic/subtopic has manual display names
        if topic not in TOPIC_DISPLAY_NAMES:
            logger.error(f"❌ Topic not in display names: {topic}")
            return []
            
        if (topic not in SUBPROJECT_DISPLAY_NAMES or 
            subtopic not in SUBPROJECT_DISPLAY_NAMES[topic]):
            logger.error(f"❌ Subtopic not in display names: {topic}/{subtopic}")
            return []
        
        # Construct file path from data directory
        filename = f"{subtopic}.csv"
        file_path = os.path.join(CONFIG["data_dir"], topic, filename)
        
        logger.info(f"📁 Loading questions from: {file_path}")
        
        if not os.path.exists(file_path):
            logger.error(f"❌ Question file not found: {file_path}")
            return []
        
        # Validate CSV format first
        if not FileManager.validate_csv_format(file_path):
            logger.error(f"❌ CSV format validation failed for: {file_path}")
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