# [file name]: file_manager.py
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
                    # Try multiple column name formats to be more flexible
                    question_text = None
                    options = []
                    correct_answer = None
                    
                    # Method 1: Check for your format (Question, Option1, Option2, Option3, Option4, Correct Answer)
                    if 'Question' in row and 'Option1' in row and 'Option2' in row and 'Option3' in row and 'Option4' in row and 'Correct Answer' in row:
                        question_text = row['Question']
                        options = [row['Option1'], row['Option2'], row['Option3'], row['Option4']]
                        correct_answer = row['Correct Answer'].strip().upper()
                    
                    # Method 2: Check for the original expected format
                    elif 'question' in row and 'option_a' in row and 'option_b' in row and 'option_c' in row and 'option_d' in row and 'correct' in row:
                        question_text = row['question']
                        options = [row['option_a'], row['option_b'], row['option_c'], row['option_d']]
                        correct_answer = row['correct'].strip().upper()
                    
                    # Method 3: Try to auto-detect columns (fallback)
                    else:
                        # Get all column names
                        columns = list(row.keys())
                        if len(columns) >= 6:  # At least Question + 4 options + correct answer
                            question_text = row[columns[0]]
                            options = [row[columns[1]], row[columns[2]], row[columns[3]], row[columns[4]]]
                            correct_answer = row[columns[5]].strip().upper()
                    
                    # Validate and process the question
                    if question_text and len(options) == 4 and correct_answer:
                        # Map correct answer to index (A=0, B=1, C=2, D=3)
                        correct_index_map = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
                        
                        if correct_answer in correct_index_map:
                            question = {
                                "question": question_text,
                                "options": options,
                                "correct_index": correct_index_map[correct_answer]
                            }
                            questions.append(question)
                        else:
                            logger.warning(f"⚠️ Invalid correct answer '{correct_answer}' in question: {question_text[:50]}...")
                    else:
                        logger.warning(f"⚠️ Skipping invalid row in {subtopic}: {row}")
            
            logger.info(f"✅ Loaded {len(questions)} questions from {file_path}")
            return questions
            
        except Exception as e:
            logger.error(f"❌ Error loading questions from {subtopic}: {e}")
            return []