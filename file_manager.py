"""
File and data management
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
        print(f"🔍 Scanning data directory: {data_dir}")
        
        if not os.path.exists(data_dir):
            print(f"❌ Data directory does not exist: {data_dir}")
            return []
        
        # List everything in data directory
        all_items = os.listdir(data_dir)
        print(f"📁 All items in data directory: {all_items}")
        
        # Filter only directories that are in our display names
        topics = []
        for item in all_items:
            item_path = os.path.join(data_dir, item)
            if os.path.isdir(item_path) and not item.startswith('.'):
                print(f"  📂 Found directory: {item}")
                if item in TOPIC_DISPLAY_NAMES:
                    print(f"  ✅ Directory '{item}' is in TOPIC_DISPLAY_NAMES")
                    topics.append(item)
                else:
                    print(f"  ❌ Directory '{item}' NOT in TOPIC_DISPLAY_NAMES")
        
        print(f"🎯 Final topics list: {topics}")
        return sorted(topics)
    
    @staticmethod
    def get_topic_display_name(topic: str) -> str:
        return TOPIC_DISPLAY_NAMES.get(topic, topic.title())
    
    @staticmethod
    @lru_cache(maxsize=128)
    def list_subtopics(topic: str) -> List[str]:
        """Get list of available subtopics for a topic"""
        print(f"🔍 Looking for subtopics in topic: '{topic}'")
        
        if not validate_topic_name(topic):
            print(f"❌ Invalid topic name: {topic}")
            return []
            
        if topic not in TOPIC_DISPLAY_NAMES:
            print(f"❌ Topic '{topic}' not in TOPIC_DISPLAY_NAMES")
            return []
        
        topic_path = os.path.join(CONFIG["data_dir"], topic)
        print(f"📁 Topic path: {topic_path}")
        
        if not os.path.exists(topic_path):
            print(f"❌ Topic path does not exist: {topic_path}")
            return []
        
        # List all files in topic directory
        all_files = os.listdir(topic_path)
        print(f"📄 All files in {topic}: {all_files}")
        
        subtopics = []
        for file in all_files:
            if file.endswith('.csv') and not file.startswith('.'):
                subtopic_name = file[:-4]  # Remove .csv extension
                print(f"  📊 Found CSV file: {file} -> subtopic: '{subtopic_name}'")
                
                if validate_subtopic_name(subtopic_name):
                    if (topic in SUBPROJECT_DISPLAY_NAMES and 
                        subtopic_name in SUBPROJECT_DISPLAY_NAMES[topic]):
                        print(f"  ✅ Subtopic '{subtopic_name}' is in SUBPROJECT_DISPLAY_NAMES")
                        subtopics.append(subtopic_name)
                    else:
                        print(f"  ❌ Subtopic '{subtopic_name}' NOT in SUBPROJECT_DISPLAY_NAMES for topic '{topic}'")
                        print(f"     Available subtopics in config: {list(SUBPROJECT_DISPLAY_NAMES.get(topic, {}).keys())}")
                else:
                    print(f"  ❌ Invalid subtopic name: '{subtopic_name}'")
        
        print(f"🎯 Final subtopics for {topic}: {subtopics}")
        return sorted(subtopics)
    
    @staticmethod
    def get_subtopic_display_name(topic: str, subtopic: str) -> str:
        if (topic in SUBPROJECT_DISPLAY_NAMES and 
            subtopic in SUBPROJECT_DISPLAY_NAMES[topic]):
            return SUBPROJECT_DISPLAY_NAMES[topic][subtopic]
        return subtopic.title()
    
    @staticmethod
    def load_questions(topic: str, subtopic: str) -> List[Dict]:
        """Load questions from CSV file in data directory"""
        print(f"🚨 LOAD_QUESTIONS called with topic='{topic}', subtopic='{subtopic}'")
        
        # Security validation
        if not validate_topic_name(topic) or not validate_subtopic_name(subtopic):
            print(f"❌ Invalid topic or subtopic name: {topic}/{subtopic}")
            return []
            
        # Check if this topic/subtopic has manual display names
        if topic not in TOPIC_DISPLAY_NAMES:
            print(f"❌ Topic '{topic}' not in TOPIC_DISPLAY_NAMES")
            return []
            
        if (topic not in SUBPROJECT_DISPLAY_NAMES or 
            subtopic not in SUBPROJECT_DISPLAY_NAMES[topic]):
            print(f"❌ Subtopic '{subtopic}' not in SUBPROJECT_DISPLAY_NAMES for topic '{topic}'")
            print(f"   Available subtopics: {list(SUBPROJECT_DISPLAY_NAMES.get(topic, {}).keys())}")
            return []
        
        # Construct file path from data directory
        filename = f"{subtopic}.csv"
        file_path = os.path.join(CONFIG["data_dir"], topic, filename)
        print(f"📁 Looking for file: {file_path}")
        
        if not os.path.exists(file_path):
            print(f"❌ Question file not found: {file_path}")
            # List what files actually exist in that directory
            topic_dir = os.path.join(CONFIG["data_dir"], topic)
            if os.path.exists(topic_dir):
                existing_files = os.listdir(topic_dir)
                print(f"📄 Existing files in {topic_dir}: {existing_files}")
            return []
        
        print(f"✅ File found: {file_path}")
        
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
                        print(f"⚠️ Invalid correct answer in row {i}: '{correct}'")
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
            
            print(f"✅ Loaded {valid_questions} valid questions from {row_count} rows in {file_path}")
            
            if valid_questions == 0:
                print(f"⚠️ No valid questions found in {file_path}")
                
        except Exception as e:
            print(f"❌ Error loading questions from {file_path}: {e}")
        
        return questions