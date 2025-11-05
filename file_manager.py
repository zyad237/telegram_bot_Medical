"""
File system navigation for 6-level curriculum structure
"""
import os
import logging
from typing import List, Optional
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