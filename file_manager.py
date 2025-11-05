"""
File system navigation for 6-level curriculum structure
"""
import os
import logging
import csv
from typing import List, Optional, Dict, Any
from config import NAVIGATION_STRUCTURE

logger = logging.getLogger(__name__)

class FileManager:
    @staticmethod
    def get_data_path(*paths) -> str:
        """Build path to data directory"""
        base_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        return os.path.join(base_dir, *paths)
    
    @staticmethod
    def list_years() -> List[str]:
        """List available years from navigation structure"""
        return list(NAVIGATION_STRUCTURE.keys())
    
    @staticmethod
    def get_year_display_name(year: str) -> str:
        """Get display name for year"""
        return NAVIGATION_STRUCTURE.get(year, {}).get("display_name", year.replace('_', ' ').title())
    
    @staticmethod
    def list_terms(year: str) -> List[str]:
        """List available terms for a year"""
        year_data = NAVIGATION_STRUCTURE.get(year, {})
        terms = year_data.get("terms", {})
        return list(terms.keys())
    
    @staticmethod
    def get_term_display_name(year: str, term: str) -> str:
        """Get display name for term"""
        year_data = NAVIGATION_STRUCTURE.get(year, {})
        term_data = year_data.get("terms", {}).get(term, {})
        return term_data.get("display_name", term.replace('_', ' ').title())
    
    @staticmethod
    def list_blocks(year: str, term: str) -> List[str]:
        """List available blocks for a term"""
        year_data = NAVIGATION_STRUCTURE.get(year, {})
        term_data = year_data.get("terms", {}).get(term, {})
        blocks = term_data.get("blocks", {})
        return list(blocks.keys())
    
    @staticmethod
    def get_block_display_name(year: str, term: str, block: str) -> str:
        """Get display name for block"""
        year_data = NAVIGATION_STRUCTURE.get(year, {})
        term_data = year_data.get("terms", {}).get(term, {})
        block_data = term_data.get("blocks", {}).get(block, {})
        return block_data.get("display_name", block.replace('_', ' ').title())
    
    @staticmethod
    def list_subjects(year: str, term: str, block: str) -> List[str]:
        """List available subjects for a block"""
        year_data = NAVIGATION_STRUCTURE.get(year, {})
        term_data = year_data.get("terms", {}).get(term, {})
        block_data = term_data.get("blocks", {}).get(block, {})
        subjects = block_data.get("subjects", {})
        return list(subjects.keys())
    
    @staticmethod
    def get_subject_display_name(year: str, term: str, block: str, subject: str) -> str:
        """Get display name for subject"""
        year_data = NAVIGATION_STRUCTURE.get(year, {})
        term_data = year_data.get("terms", {}).get(term, {})
        block_data = term_data.get("blocks", {}).get(block, {})
        subject_data = block_data.get("subjects", {}).get(subject, {})
        return subject_data.get("display_name", subject.replace('_', ' ').title())
    
    @staticmethod
    def list_categories(year: str, term: str, block: str, subject: str) -> List[str]:
        """List available categories for a subject"""
        year_data = NAVIGATION_STRUCTURE.get(year, {})
        term_data = year_data.get("terms", {}).get(term, {})
        block_data = term_data.get("blocks", {}).get(block, {})
        subject_data = block_data.get("subjects", {}).get(subject, {})
        categories = subject_data.get("categories", {})
        return list(categories.keys())
    
    @staticmethod
    def get_category_display_name(year: str, term: str, block: str, subject: str, category: str) -> str:
        """Get display name for category"""
        year_data = NAVIGATION_STRUCTURE.get(year, {})
        term_data = year_data.get("terms", {}).get(term, {})
        block_data = term_data.get("blocks", {}).get(block, {})
        subject_data = block_data.get("subjects", {}).get(subject, {})
        category_data = subject_data.get("categories", {}).get(category, {})
        return category_data.get("display_name", category.replace('_', ' ').title())
    
    @staticmethod
    def list_subtopics(year: str, term: str, block: str, subject: str, category: str) -> List[str]:
        """List available subtopics for a category"""
        year_data = NAVIGATION_STRUCTURE.get(year, {})
        term_data = year_data.get("terms", {}).get(term, {})
        block_data = term_data.get("blocks", {}).get(block, {})
        subject_data = block_data.get("subjects", {}).get(subject, {})
        category_data = subject_data.get("categories", {}).get(category, {})
        subtopics = category_data.get("subtopics", {})
        return list(subtopics.keys())
    
    @staticmethod
    def get_subtopic_display_name(year: str, term: str, block: str, subject: str, category: str, subtopic: str) -> str:
        """Get display name for subtopic"""
        year_data = NAVIGATION_STRUCTURE.get(year, {})
        term_data = year_data.get("terms", {}).get(term, {})
        block_data = term_data.get("blocks", {}).get(block, {})
        subject_data = block_data.get("subjects", {}).get(subject, {})
        category_data = subject_data.get("categories", {}).get(category, {})
        subtopics = category_data.get("subtopics", {})
        return subtopics.get(subtopic, subtopic.replace('_', ' ').title())
    
    @staticmethod
    def get_subtopic_file_path(year: str, term: str, block: str, subject: str, category: str, subtopic: str) -> Optional[str]:
        """Get the file path for a subtopic"""
        year_data = NAVIGATION_STRUCTURE.get(year, {})
        term_data = year_data.get("terms", {}).get(term, {})
        block_data = term_data.get("blocks", {}).get(block, {})
        subject_data = block_data.get("subjects", {}).get(subject, {})
        category_data = subject_data.get("categories", {}).get(category, {})
        
        # Get the actual filename from the subtopics mapping
        subtopics = category_data.get("subtopics", {})
        filename = subtopic  # This is the key in the subtopics dict
        
        # Build the file path
        file_path = FileManager.get_data_path(year, term, block, subject, category, filename)
        
        if os.path.exists(file_path):
            return file_path
        else:
            logger.warning(f"File not found: {file_path}")
            return None

    @staticmethod
    def load_questions(year: str, term: str, block: str, subject: str, category: str, subtopic: str) -> List[Dict[str, Any]]:
        """
        Load questions from CSV file - matches QuizManager expectations
        
        Expected CSV format:
        question,option1,option2,option3,option4,correct_answer,explanation
        
        Returns format that QuizManager expects:
        {
            "question": "text",
            "options": ["opt1", "opt2", "opt3", "opt4"],
            "correct_index": 0,
            "explanation": "text"
        }
        """
        questions = []
        
        # Get file path using navigation parameters
        file_path = FileManager.get_subtopic_file_path(year, term, block, subject, category, subtopic)
        
        if not file_path:
            logger.error(f"❌ CSV file not found: {file_path}")
            return questions
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                
                for row_num, row in enumerate(csv_reader, 1):
                    # Validate required fields
                    if not row.get('question') or not row.get('correct_answer'):
                        logger.warning(f"⚠️ Skipping row {row_num}: missing question or correct_answer")
                        continue
                    
                    # Build options list
                    options = []
                    for i in range(1, 5):
                        option_key = f'option{i}'
                        if option_key in row and row[option_key]:
                            options.append(row[option_key])
                    
                    if len(options) < 2:
                        logger.warning(f"⚠️ Skipping row {row_num}: insufficient options")
                        continue
                    
                    # Find correct index
                    correct_answer = row['correct_answer']
                    correct_index = -1
                    
                    # Try exact match first
                    if correct_answer in options:
                        correct_index = options.index(correct_answer)
                    else:
                        # Try matching by letter (A, B, C, D)
                        letter_map = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
                        if correct_answer.upper() in letter_map:
                            correct_index = letter_map[correct_answer.upper()]
                    
                    if correct_index == -1:
                        logger.warning(f"⚠️ Skipping row {row_num}: could not find correct answer '{correct_answer}' in options")
                        continue
                    
                    question_data = {
                        'question': row['question'],
                        'options': options,
                        'correct_index': correct_index,
                        'explanation': row.get('explanation', 'No explanation provided.')
                    }
                    
                    questions.append(question_data)
                
                logger.info(f"✅ Loaded {len(questions)} questions from {file_path}")
                
        except Exception as e:
            logger.error(f"❌ Error loading questions from {file_path}: {e}")
        
        return questions