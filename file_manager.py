"""
File management for medical curriculum structure
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
    # ... (keep all the list_years, list_terms, list_blocks, list_subjects, list_categories methods the same)
    
    @staticmethod
    @lru_cache(maxsize=1024)
    def list_subtopics(year: str, term: str, block: str, subject: str, category: str) -> List[str]:
        """Get list of available subtopics for a category - using actual filenames"""
        structure = NAVIGATION_STRUCTURE
        if (year not in structure or 
            "terms" not in structure[year] or
            term not in structure[year]["terms"] or
            "blocks" not in structure[year]["terms"][term] or
            block not in structure[year]["terms"][term]["blocks"] or
            "subjects" not in structure[year]["terms"][term]["blocks"][block] or
            subject not in structure[year]["terms"][term]["blocks"][block]["subjects"] or
            "categories" not in structure[year]["terms"][term]["blocks"][block]["subjects"][subject] or
            category not in structure[year]["terms"][term]["blocks"][block]["subjects"][subject]["categories"]):
            return []
        
        category_path = os.path.join(CONFIG["data_dir"], year, term, block, subject, category)
        if not os.path.exists(category_path):
            return []
        
        subtopics = []
        for file in os.listdir(category_path):
            if file.endswith('.csv') and not file.startswith('.'):
                # Use the actual filename as the subtopic key
                if ("subtopics" in structure[year]["terms"][term]["blocks"][block]["subjects"][subject]["categories"][category] and
                    file in structure[year]["terms"][term]["blocks"][block]["subjects"][subject]["categories"][category]["subtopics"]):
                    subtopics.append(file)  # Store the full filename
        
        return sorted(subtopics)
    
    @staticmethod
    def get_subtopic_display_name(year: str, term: str, block: str, subject: str, category: str, subtopic: str) -> str:
        """Get display name for subtopic - subtopic is the actual filename"""
        structure = NAVIGATION_STRUCTURE
        if (year in structure and 
            "terms" in structure[year] and
            term in structure[year]["terms"] and
            "blocks" in structure[year]["terms"][term] and
            block in structure[year]["terms"][term]["blocks"] and
            "subjects" in structure[year]["terms"][term]["blocks"][block] and
            subject in structure[year]["terms"][term]["blocks"][block]["subjects"] and
            "categories" in structure[year]["terms"][term]["blocks"][block]["subjects"][subject] and
            category in structure[year]["terms"][term]["blocks"][block]["subjects"][subject]["categories"] and
            "subtopics" in structure[year]["terms"][term]["blocks"][block]["subjects"][subject]["categories"][category] and
            subtopic in structure[year]["terms"][term]["blocks"][block]["subjects"][subject]["categories"][category]["subtopics"]):
            return structure[year]["terms"][term]["blocks"][block]["subjects"][subject]["categories"][category]["subtopics"][subtopic]
        
        # Fallback: remove .csv and format the filename
        return subtopic[:-4].replace('_', ' ').title()
    
    @staticmethod
    def load_questions(year: str, term: str, block: str, subject: str, category: str, subtopic: str) -> List[Dict]:
        """Load questions from CSV file - subtopic is the actual filename"""
        structure = NAVIGATION_STRUCTURE
        
        # Check if this path exists in navigation structure
        if (year not in structure or 
            "terms" not in structure[year] or
            term not in structure[year]["terms"] or
            "blocks" not in structure[year]["terms"][term] or
            block not in structure[year]["terms"][term]["blocks"] or
            "subjects" not in structure[year]["terms"][term]["blocks"][block] or
            subject not in structure[year]["terms"][term]["blocks"][block]["subjects"] or
            "categories" not in structure[year]["terms"][term]["blocks"][block]["subjects"][subject] or
            category not in structure[year]["terms"][term]["blocks"][block]["subjects"][subject]["categories"] or
            "subtopics" not in structure[year]["terms"][term]["blocks"][block]["subjects"][subject]["categories"][category] or
            subtopic not in structure[year]["terms"][term]["blocks"][block]["subjects"][subject]["categories"][category]["subtopics"]):
            logger.error(f"❌ Path not in navigation structure: {year}/{term}/{block}/{subject}/{category}/{subtopic}")
            return []
        
        # Construct file path - subtopic is already the filename
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