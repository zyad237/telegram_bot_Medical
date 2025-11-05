"""
Universal file management for quiz data - finds CSV files regardless of directory structure
"""
import os
import csv
import logging
from typing import List, Dict, Optional
from config import CONFIG, NAVIGATION_STRUCTURE

logger = logging.getLogger(__name__)

class FileManager:
    
    # Cache for found CSV files to avoid repeated scanning
    _csv_cache = None
    
    @staticmethod
    def _scan_all_csv_files() -> Dict[str, str]:
        """Scan entire data directory and build a mapping of filenames to full paths"""
        if FileManager._csv_cache is not None:
            return FileManager._csv_cache
            
        csv_cache = {}
        data_dir = CONFIG["data_dir"]
        
        if not os.path.exists(data_dir):
            logger.error(f"❌ Data directory not found: {data_dir}")
            return {}
        
        logger.info("🔍 Scanning for CSV files...")
        for root, dirs, files in os.walk(data_dir):
            for file in files:
                if file.endswith('.csv'):
                    full_path = os.path.join(root, file)
                    # Store both with and without spaces for flexible lookup
                    csv_cache[file] = full_path
                    csv_cache[file.replace(' ', '')] = full_path
                    csv_cache[file.replace(' ', '_')] = full_path
                    
                    # Also store with just the number part for callback matching
                    base_name = os.path.splitext(file)[0]
                    if '_' in base_name:
                        number_part = base_name.split('_')[0]
                        csv_cache[number_part + '.csv'] = full_path
        
        logger.info(f"✅ Found {len([k for k in csv_cache.keys() if not k.endswith(('.csv', '_csv'))])} unique CSV files")
        FileManager._csv_cache = csv_cache
        return csv_cache
    
    @staticmethod
    def _find_csv_file_anywhere(filename: str) -> Optional[str]:
        """Find CSV file anywhere in the data directory"""
        cache = FileManager._scan_all_csv_files()
        
        # Try exact match first
        if filename in cache:
            return cache[filename]
        
        # Try without spaces
        filename_no_spaces = filename.replace(' ', '')
        if filename_no_spaces in cache:
            return cache[filename_no_spaces]
        
        # Try with underscores
        filename_underscores = filename.replace(' ', '_')
        if filename_underscores in cache:
            return cache[filename_underscores]
        
        # Try to match by number
        base_name = os.path.splitext(filename)[0]
        number_part = base_name.split('_')[0] if '_' in base_name else base_name
        
        for cached_file, full_path in cache.items():
            if cached_file.startswith(number_part + '_') or cached_file.startswith(number_part + ' '):
                return full_path
        
        logger.error(f"❌ CSV file not found anywhere: {filename}")
        logger.info(f"📁 Available files: {list(set([k for k in cache.keys() if k.endswith('.csv')]))}")
        return None

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
            return list(path["subtopics"].keys())
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
        """Load questions from CSV file - uses universal file finder"""
        try:
            # Find the CSV file anywhere in the data directory
            csv_path = FileManager._find_csv_file_anywhere(subtopic)
            
            if not csv_path:
                logger.error(f"❌ CSV file not found: {subtopic}")
                return []
            
            logger.info(f"📖 Loading questions from: {csv_path}")
            
            questions = []
            with open(csv_path, 'r', encoding='utf-8') as file:
                # Try different encodings if utf-8 fails
                try:
                    file.seek(0)
                    reader = csv.DictReader(file)
                    rows = list(reader)
                except UnicodeDecodeError:
                    logger.warning("⚠️ UTF-8 failed, trying latin-1")
                    with open(csv_path, 'r', encoding='latin-1') as file2:
                        reader = csv.DictReader(file2)
                        rows = list(reader)
                except Exception as e:
                    logger.error(f"❌ Error reading CSV: {e}")
                    return []
                
                for i, row in enumerate(rows):
                    # Try multiple column name formats to be more flexible
                    question_text = None
                    options = []
                    correct_answer = None
                    
                    # Method 1: Check for your format (Question, Option1, Option2, Option3, Option4, Correct Answer)
                    if 'Question' in row and 'Option1' in row and 'Option2' in row and 'Option3' in row and 'Option4' in row and 'Correct Answer' in row:
                        question_text = row['Question'].strip()
                        options = [
                            row['Option1'].strip(),
                            row['Option2'].strip(), 
                            row['Option3'].strip(),
                            row['Option4'].strip()
                        ]
                        correct_answer = row['Correct Answer'].strip().upper()
                    
                    # Method 2: Check for the original expected format
                    elif 'question' in row and 'option_a' in row and 'option_b' in row and 'option_c' in row and 'option_d' in row and 'correct' in row:
                        question_text = row['question'].strip()
                        options = [
                            row['option_a'].strip(),
                            row['option_b'].strip(),
                            row['option_c'].strip(),
                            row['option_d'].strip()
                        ]
                        correct_answer = row['correct'].strip().upper()
                    
                    # Method 3: Try to auto-detect columns (fallback)
                    else:
                        # Get all column names
                        columns = list(row.keys())
                        if len(columns) >= 6:  # At least Question + 4 options + correct answer
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
                        # Remove empty options and check we still have 4
                        options = [opt for opt in options if opt]
                        
                        if len(options) == 4:
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
                                logger.warning(f"⚠️ Row {i+1}: Invalid correct answer '{correct_answer}' - must be A, B, C, or D")
                        else:
                            logger.warning(f"⚠️ Row {i+1}: Not enough valid options (need 4, got {len(options)})")
                    else:
                        logger.warning(f"⚠️ Row {i+1}: Missing question text, options, or correct answer")
            
            logger.info(f"✅ Loaded {len(questions)} valid questions from {os.path.basename(csv_path)}")
            return questions
            
        except Exception as e:
            logger.error(f"❌ Error loading questions from {subtopic}: {e}")
            return []