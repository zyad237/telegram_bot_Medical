# [file name]: file_manager.py
"""
Simplified file management for quiz data with automated navigation
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
        if path and "subtopics" in path:
            # Return the actual CSV filenames from the navigation structure
            return list(path["subtopics"].keys())
        
        # Fallback: try to find files in the directory
        category_path = os.path.join(CONFIG["data_dir"], year, term, block, subject, category)
        if os.path.exists(category_path):
            csv_files = [f for f in os.listdir(category_path) if f.endswith('.csv')]
            return sorted(csv_files)
        
        return []
    
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
        """Load questions from CSV file using simple path structure"""
        try:
            # Construct file path: data/year/term/block/subject/category/filename.csv
            file_path = os.path.join(CONFIG["data_dir"], year, term, block, subject, category, subtopic)
            
            logger.info(f"🔍 Looking for file: {file_path}")
            
            if not os.path.exists(file_path):
                logger.error(f"❌ File not found: {file_path}")
                
                # Try alternative path structures
                alternative_paths = [
                    os.path.join(CONFIG["data_dir"], year, subject, category, subtopic),
                    os.path.join(CONFIG["data_dir"], year, category, subtopic),
                    os.path.join(CONFIG["data_dir"], subject, category, subtopic),
                    os.path.join(CONFIG["data_dir"], category, subtopic),
                ]
                
                for alt_path in alternative_paths:
                    if os.path.exists(alt_path):
                        file_path = alt_path
                        logger.info(f"✅ Using alternative path: {alt_path}")
                        break
                else:
                    logger.error(f"❌ File not found in any alternative path: {subtopic}")
                    # List what's actually in the directory for debugging
                    expected_dir = os.path.join(CONFIG["data_dir"], year, term, block, subject, category)
                    if os.path.exists(expected_dir):
                        actual_files = os.listdir(expected_dir)
                        logger.info(f"📁 Files in {expected_dir}: {actual_files}")
                    return []
            
            logger.info(f"📖 Loading questions from: {file_path}")
            
            questions = []
            with open(file_path, 'r', encoding='utf-8') as file:
                # Try different encodings if utf-8 fails
                try:
                    file.seek(0)
                    reader = csv.DictReader(file)
                    rows = list(reader)
                except UnicodeDecodeError:
                    logger.warning("⚠️ UTF-8 failed, trying latin-1")
                    with open(file_path, 'r', encoding='latin-1') as file2:
                        reader = csv.DictReader(file2)
                        rows = list(reader)
                except Exception as e:
                    logger.error(f"❌ Error reading CSV: {e}")
                    return []
                
                for i, row in enumerate(rows):
                    # Try multiple column name formats
                    question_text = None
                    options = []
                    correct_answer = None
                    
                    # Method 1: Your format (Question, Option1, Option2, Option3, Option4, Correct Answer)
                    if 'Question' in row and 'Option1' in row and 'Option2' in row and 'Option3' in row and 'Option4' in row and 'Correct Answer' in row:
                        question_text = row['Question'].strip()
                        options = [
                            row['Option1'].strip(),
                            row['Option2'].strip(), 
                            row['Option3'].strip(),
                            row['Option4'].strip()
                        ]
                        correct_answer = row['Correct Answer'].strip().upper()
                    
                    # Method 2: Original format
                    elif 'question' in row and 'option_a' in row and 'option_b' in row and 'option_c' in row and 'option_d' in row and 'correct' in row:
                        question_text = row['question'].strip()
                        options = [
                            row['option_a'].strip(),
                            row['option_b'].strip(),
                            row['option_c'].strip(),
                            row['option_d'].strip()
                        ]
                        correct_answer = row['correct'].strip().upper()
                    
                    # Method 3: Auto-detect columns
                    else:
                        columns = list(row.keys())
                        if len(columns) >= 6:
                            question_text = row[columns[0]].strip()
                            options = [
                                row[columns[1]].strip(),
                                row[columns[2]].strip(),
                                row[columns[3]].strip(),
                                row[columns[4]].strip()
                            ]
                            correct_answer = row[columns[5]].strip().upper()
                        else:
                            logger.warning(f"⚠️ Row {i+1}: Not enough columns (need 6, got {len(columns)})")
                            continue
                    
                    # Validate and process the question
                    if question_text and len(options) == 4 and correct_answer:
                        options = [opt for opt in options if opt]
                        
                        if len(options) == 4:
                            correct_index_map = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
                            
                            if correct_answer in correct_index_map:
                                question = {
                                    "question": question_text,
                                    "options": options,
                                    "correct_index": correct_index_map[correct_answer]
                                }
                                questions.append(question)
                            else:
                                logger.warning(f"⚠️ Row {i+1}: Invalid correct answer '{correct_answer}'")
                        else:
                            logger.warning(f"⚠️ Row {i+1}: Not enough valid options (need 4, got {len(options)})")
                    else:
                        logger.warning(f"⚠️ Row {i+1}: Missing data")
            
            logger.info(f"✅ Loaded {len(questions)} questions from {os.path.basename(file_path)}")
            return questions
            
        except Exception as e:
            logger.error(f"❌ Error loading questions from {subtopic}: {e}")
            return []
