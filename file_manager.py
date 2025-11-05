"""
File management for 6-level navigation structure
"""
import os
import csv
import logging
from typing import List, Dict
from functools import lru_cache

from config import CONFIG, NAVIGATION_STRUCTURE
from utils import sanitize_text

logger = logging.getLogger(__name__)

class FileManager:
    @staticmethod
    @lru_cache(maxsize=32)
    def list_years() -> List[str]:
        """Get list of available years from data directory"""
        data_dir = CONFIG["data_dir"]
        if not os.path.exists(data_dir):
            return []
        
        years = [d for d in os.listdir(data_dir) 
                if os.path.isdir(os.path.join(data_dir, d)) 
                and not d.startswith('.')
                and d in NAVIGATION_STRUCTURE]
        return sorted(years)
    
    @staticmethod
    def get_year_display_name(year: str) -> str:
        """Get display name for year"""
        return NAVIGATION_STRUCTURE.get(year, {}).get("display_name", year.replace('_', ' ').title())
    
    @staticmethod
    @lru_cache(maxsize=64)
    def list_terms(year: str) -> List[str]:
        """Get list of available terms for a year"""
        if year not in NAVIGATION_STRUCTURE or "terms" not in NAVIGATION_STRUCTURE[year]:
            return []
        
        year_path = os.path.join(CONFIG["data_dir"], year)
        if not os.path.exists(year_path):
            return []
        
        terms = [t for t in os.listdir(year_path) 
                if os.path.isdir(os.path.join(year_path, t))
                and not t.startswith('.')
                and t in NAVIGATION_STRUCTURE[year]["terms"]]
        return sorted(terms)
    
    @staticmethod
    def get_term_display_name(year: str, term: str) -> str:
        """Get display name for term"""
        if (year in NAVIGATION_STRUCTURE and 
            "terms" in NAVIGATION_STRUCTURE[year] and
            term in NAVIGATION_STRUCTURE[year]["terms"]):
            return NAVIGATION_STRUCTURE[year]["terms"][term]["display_name"]
        return term.replace('_', ' ').title()
    
    @staticmethod
    @lru_cache(maxsize=128)
    def list_blocks(year: str, term: str) -> List[str]:
        """Get list of available blocks for a term"""
        if (year not in NAVIGATION_STRUCTURE or 
            "terms" not in NAVIGATION_STRUCTURE[year] or
            term not in NAVIGATION_STRUCTURE[year]["terms"]):
            return []
        
        term_path = os.path.join(CONFIG["data_dir"], year, term)
        if not os.path.exists(term_path):
            return []
        
        blocks = [b for b in os.listdir(term_path)
                 if os.path.isdir(os.path.join(term_path, b))
                 and not b.startswith('.')
                 and "blocks" in NAVIGATION_STRUCTURE[year]["terms"][term]
                 and b in NAVIGATION_STRUCTURE[year]["terms"][term]["blocks"]]
        return sorted(blocks)
    
    @staticmethod
    def get_block_display_name(year: str, term: str, block: str) -> str:
        """Get display name for block"""
        if (year in NAVIGATION_STRUCTURE and 
            "terms" in NAVIGATION_STRUCTURE[year] and
            term in NAVIGATION_STRUCTURE[year]["terms"] and
            "blocks" in NAVIGATION_STRUCTURE[year]["terms"][term] and
            block in NAVIGATION_STRUCTURE[year]["terms"][term]["blocks"]):
            return NAVIGATION_STRUCTURE[year]["terms"][term]["blocks"][block]["display_name"]
        return block.replace('_', ' ').title()
    
    @staticmethod
    @lru_cache(maxsize=256)
    def list_subjects(year: str, term: str, block: str) -> List[str]:
        """Get list of available subjects for a block"""
        if (year not in NAVIGATION_STRUCTURE or 
            "terms" not in NAVIGATION_STRUCTURE[year] or
            term not in NAVIGATION_STRUCTURE[year]["terms"] or
            "blocks" not in NAVIGATION_STRUCTURE[year]["terms"][term] or
            block not in NAVIGATION_STRUCTURE[year]["terms"][term]["blocks"]):
            return []
        
        block_path = os.path.join(CONFIG["data_dir"], year, term, block)
        if not os.path.exists(block_path):
            return []
        
        subjects = [s for s in os.listdir(block_path)
                   if os.path.isdir(os.path.join(block_path, s))
                   and not s.startswith('.')
                   and "subjects" in NAVIGATION_STRUCTURE[year]["terms"][term]["blocks"][block]
                   and s in NAVIGATION_STRUCTURE[year]["terms"][term]["blocks"][block]["subjects"]]
        return sorted(subjects)
    
    @staticmethod
    def get_subject_display_name(year: str, term: str, block: str, subject: str) -> str:
        """Get display name for subject"""
        if (year in NAVIGATION_STRUCTURE and 
            "terms" in NAVIGATION_STRUCTURE[year] and
            term in NAVIGATION_STRUCTURE[year]["terms"] and
            "blocks" in NAVIGATION_STRUCTURE[year]["terms"][term] and
            block in NAVIGATION_STRUCTURE[year]["terms"][term]["blocks"] and
            "subjects" in NAVIGATION_STRUCTURE[year]["terms"][term]["blocks"][block] and
            subject in NAVIGATION_STRUCTURE[year]["terms"][term]["blocks"][block]["subjects"]):
            return NAVIGATION_STRUCTURE[year]["terms"][term]["blocks"][block]["subjects"][subject]["display_name"]
        return subject.title()
    
    @staticmethod
    @lru_cache(maxsize=512)
    def list_categories(year: str, term: str, block: str, subject: str) -> List[str]:
        """Get list of available categories for a subject - SIMPLIFIED VERSION"""
        if (year not in NAVIGATION_STRUCTURE or 
            "terms" not in NAVIGATION_STRUCTURE[year] or
            term not in NAVIGATION_STRUCTURE[year]["terms"] or
            "blocks" not in NAVIGATION_STRUCTURE[year]["terms"][term] or
            block not in NAVIGATION_STRUCTURE[year]["terms"][term]["blocks"] or
            "subjects" not in NAVIGATION_STRUCTURE[year]["terms"][term]["blocks"][block] or
            subject not in NAVIGATION_STRUCTURE[year]["terms"][term]["blocks"][block]["subjects"]):
            return []
        
        subject_path = os.path.join(CONFIG["data_dir"], year, term, block, subject)
        
        if not os.path.exists(subject_path):
            return []
        
        # Get ALL directories in subject path
        all_dirs = [d for d in os.listdir(subject_path) 
                   if os.path.isdir(os.path.join(subject_path, d)) and not d.startswith('.')]
        
        # Return directories that match config (case-insensitive)
        expected_categories = NAVIGATION_STRUCTURE[year]["terms"][term]["blocks"][block]["subjects"][subject]["categories"].keys()
        
        # Case-insensitive matching
        categories = []
        for dir_name in all_dirs:
            for expected_category in expected_categories:
                if dir_name.lower() == expected_category.lower():
                    categories.append(dir_name)
                    break
        
        return sorted(categories)
    
    @staticmethod
    def get_category_display_name(year: str, term: str, block: str, subject: str, category: str) -> str:
        """Get display name for category"""
        structure = NAVIGATION_STRUCTURE
        if (year in structure and 
            "terms" in structure[year] and
            term in structure[year]["terms"] and
            "blocks" in structure[year]["terms"][term] and
            block in structure[year]["terms"][term]["blocks"] and
            "subjects" in structure[year]["terms"][term]["blocks"][block] and
            subject in structure[year]["terms"][term]["blocks"][block]["subjects"] and
            "categories" in structure[year]["terms"][term]["blocks"][block]["subjects"][subject]):
            
            # Case-insensitive lookup
            for config_category, config_data in structure[year]["terms"][term]["blocks"][block]["subjects"][subject]["categories"].items():
                if config_category.lower() == category.lower():
                    return config_data["display_name"]
        
        return category.title()
    
    @staticmethod
    @lru_cache(maxsize=1024)
    def list_subtopics(year: str, term: str, block: str, subject: str, category: str) -> List[str]:
        """Get list of available subtopics for a category - SIMPLIFIED VERSION"""
        structure = NAVIGATION_STRUCTURE
        if (year not in structure or 
            "terms" not in structure[year] or
            term not in structure[year]["terms"] or
            "blocks" not in structure[year]["terms"][term] or
            block not in structure[year]["terms"][term]["blocks"] or
            "subjects" not in structure[year]["terms"][term]["blocks"][block] or
            subject not in structure[year]["terms"][term]["blocks"][block]["subjects"] or
            "categories" not in structure[year]["terms"][term]["blocks"][block]["subjects"][subject]):
            return []
        
        category_path = os.path.join(CONFIG["data_dir"], year, term, block, subject, category)
        
        if not os.path.exists(category_path):
            return []
        
        # Get ALL CSV files in category path
        all_csv_files = [f for f in os.listdir(category_path) if f.endswith('.csv') and not f.startswith('.')]
        
        # Get expected files from config (case-insensitive matching)
        expected_files = []
        for config_category, config_data in structure[year]["terms"][term]["blocks"][block]["subjects"][subject]["categories"].items():
            if config_category.lower() == category.lower():
                expected_files = list(config_data["subtopics"].keys())
                break
        
        # Return files that match expected files (case-insensitive)
        matching_files = []
        for csv_file in all_csv_files:
            for expected_file in expected_files:
                if csv_file.lower() == expected_file.lower():
                    matching_files.append(csv_file)
                    break
        
        # Sort by numeric prefix
        return sorted(matching_files, key=lambda x: (
            int(x.split('_')[0]) if x.split('_')[0].isdigit() else float('inf'), 
            x
        ))
    
    @staticmethod
    def get_subtopic_display_name(year: str, term: str, block: str, subject: str, category: str, subtopic: str) -> str:
        """Get display name for subtopic"""
        structure = NAVIGATION_STRUCTURE
        if (year in structure and 
            "terms" in structure[year] and
            term in structure[year]["terms"] and
            "blocks" in structure[year]["terms"][term] and
            block in structure[year]["terms"][term]["blocks"] and
            "subjects" in structure[year]["terms"][term]["blocks"][block] and
            subject in structure[year]["terms"][term]["blocks"][block]["subjects"] and
            "categories" in structure[year]["terms"][term]["blocks"][block]["subjects"][subject]):
            
            # Case-insensitive lookup
            for config_category, category_data in structure[year]["terms"][term]["blocks"][block]["subjects"][subject]["categories"].items():
                if config_category.lower() == category.lower():
                    for config_subtopic, display_name in category_data["subtopics"].items():
                        if config_subtopic.lower() == subtopic.lower():
                            return display_name
        
        # Fallback
        display_name = subtopic[:-4] if subtopic.endswith('.csv') else subtopic
        if '_' in display_name:
            display_name = display_name.split('_', 1)[1]
        return display_name.replace('_', ' ').title()
    
    @staticmethod
    def load_questions(year: str, term: str, block: str, subject: str, category: str, subtopic: str) -> List[Dict]:
        """Load questions from CSV file"""
        # Construct file path
        file_path = os.path.join(CONFIG["data_dir"], year, term, block, subject, category, subtopic)
        
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