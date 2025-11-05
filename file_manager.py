# [file name]: file_manager.py
[file content begin]
"""
File management for quiz data with 6-level navigation
"""
import os
import csv
import logging
from typing import List, Dict, Optional
from config import CONFIG, NAVIGATION_STRUCTURE

logger = logging.getLogger(__name__)

class FileManager:
    
    @staticmethod
    def get_navigation_path(year: str, term: str = None, block: str = None, 
                           subject: str = None, category: str = None) -> Optional[Dict]:
        """Get navigation path from structure"""
        try:
            path = NAVIGATION_STRUCTURE.get(year)
            if not path:
                return None
            
            if term:
                path = path["terms"].get(term)
                if not path:
                    return None
                
            if block:
                path = path["blocks"].get(block)
                if not path:
                    return None
                    
            if subject:
                path = path["subjects"].get(subject)
                if not path:
                    return None
                    
            if category:
                path = path["categories"].get(category)
                
            return path
            
        except (KeyError, TypeError):
            return None
    
    @staticmethod
    def list_years() -> List[str]:
        """List available years"""
        return list(NAVIGATION_STRUCTURE.keys())
    
    @staticmethod
    def list_terms(year: str) -> List[str]:
        """List available terms for a year"""
        path = FileManager.get_navigation_path(year)
        return list(path["terms"].keys()) if path and "terms" in path else []
    
    @staticmethod
    def list_blocks(year: str, term: str) -> List[str]:
        """List available blocks for a term"""
        path = FileManager.get_navigation_path(year, term)
        return list(path["blocks"].keys()) if path and "blocks" in path else []
    
    @staticmethod
    def list_subjects(year: str, term: str, block: str) -> List[str]:
        """List available subjects for a block"""
        path = FileManager.get_navigation_path(year, term, block)
        return list(path["subjects"].keys()) if path and "subjects" in path else []
    
    @staticmethod
    def list_categories(year: str, term: str, block: str, subject: str) -> List[str]:
        """List available categories for a subject"""
        path = FileManager.get_navigation_path(year, term, block, subject)
        return list(path["categories"].keys()) if path and "categories" in path else []
    
    @staticmethod
    def list_subtopics(year: str, term: str, block: str, subject: str, category: str) -> List[str]:
        """List available subtopics for a category"""
        path = FileManager.get_navigation_path(year, term, block, subject, category)
        return list(path["subtopics"].keys()) if path and "subtopics" in path else []
    
    @staticmethod
    def get_year_display_name(year: str) -> str:
        """Get display name for year"""
        path = FileManager.get_navigation_path(year)
        return path["display_name"] if path and "display_name" in path else year
    
    @staticmethod
    def get_term_display_name(year: str, term: str) -> str:
        """Get display name for term"""
        path = FileManager.get_navigation_path(year, term)
        return path["display_name"] if path and "display_name" in path else term
    
    @staticmethod
    def get_block_display_name(year: str, term: str, block: str) -> str:
        """Get display name for block"""
        path = FileManager.get_navigation_path(year, term, block)
        return path["display_name"] if path and "display_name" in path else block
    
    @staticmethod
    def get_subject_display_name(year: str, term: str, block: str, subject: str) -> str:
        """Get display name for subject"""
        path = FileManager.get_navigation_path(year, term, block, subject)
        return path["display_name"] if path and "display_name" in path else subject
    
    @staticmethod
    def get_category_display_name(year: str, term: str, block: str, subject: str, category: str) -> str:
        """Get display name for category"""
        path = FileManager.get_navigation_path(year, term, block, subject, category)
        return path["display_name"] if path and "display_name" in path else category
    
    @staticmethod
    def get_subtopic_display_name(year: str, term: str, block: str, subject: str, category: str, subtopic: str) -> str:
        """Get display name for subtopic"""
        path = FileManager.get_navigation_path(year, term, block, subject, category)
        if path and "subtopics" in path and subtopic in path["subtopics"]:
            return path["subtopics"][subtopic]
        return subtopic
    
    @staticmethod
    def load_questions(year: str, term: str, block: str, subject: str, category: str, subtopic: str) -> List[Dict]:
        """Load questions from CSV file"""
        try:
            # Construct file path
            file_path = os.path.join(
                CONFIG["data_dir"], year, term, block, subject, category, subtopic
            )
            
            if not os.path.exists(file_path):
                logger.error(f"❌ File not found: {file_path}")
                return []
            
            questions = []
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    if all(key in row for key in ['question', 'option_a', 'option_b', 'option_c', 'option_d', 'correct']):
                        question = {
                            "question": row['question'],
                            "options": [
                                row['option_a'],
                                row['option_b'], 
                                row['option_c'],
                                row['option_d']
                            ],
                            "correct_index": ['a', 'b', 'c', 'd'].index(row['correct'].lower())
                        }
                        questions.append(question)
            
            logger.info(f"✅ Loaded {len(questions)} questions from {file_path}")
            return questions
            
        except Exception as e:
            logger.error(f"❌ Error loading questions from {subtopic}: {e}")
            return []
[file content end]