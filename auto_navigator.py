# [file name]: auto_navigator.py
"""
Automated navigation structure builder - scans data directory and builds navigation dynamically
"""
import os
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class AutoNavigator:
    
    @staticmethod
    def build_navigation_structure(data_dir: str = "data") -> Dict:
        """Scan data directory and build complete navigation structure automatically"""
        
        if not os.path.exists(data_dir):
            logger.error(f"❌ Data directory not found: {data_dir}")
            return {}
        
        logger.info("🏗️ Building navigation structure from data directory...")
        
        # Initialize structure
        structure = {}
        
        # Scan all directories and files
        for root, dirs, files in os.walk(data_dir):
            # Skip the root data directory itself
            if root == data_dir:
                continue
                
            # Get relative path from data directory
            rel_path = os.path.relpath(root, data_dir)
            path_parts = rel_path.split(os.sep)
            
            logger.debug(f"📁 Scanning: {rel_path} (levels: {len(path_parts)})")
            
            # Build structure based on directory depth
            if len(path_parts) == 1:
                # Year level: year_1
                year = path_parts[0]
                structure[year] = AutoNavigator._create_year_node(year, os.path.join(data_dir, year))
                
            elif len(path_parts) == 2:
                # Term level: year_1/term_1
                year, term = path_parts
                if year in structure:
                    structure[year]["terms"][term] = AutoNavigator._create_term_node(term, os.path.join(data_dir, year, term))
                    
            elif len(path_parts) == 3:
                # Block level: year_1/term_1/block_1
                year, term, block = path_parts
                if year in structure and term in structure[year]["terms"]:
                    structure[year]["terms"][term]["blocks"][block] = \
                        AutoNavigator._create_block_node(block, os.path.join(data_dir, year, term, block))
                    
            elif len(path_parts) == 4:
                # Subject level: year_1/term_1/block_1/anatomy
                year, term, block, subject = path_parts
                if (year in structure and 
                    term in structure[year]["terms"] and 
                    block in structure[year]["terms"][term]["blocks"]):
                    structure[year]["terms"][term]["blocks"][block]["subjects"][subject] = \
                        AutoNavigator._create_subject_node(subject, os.path.join(data_dir, year, term, block, subject))
                    
            elif len(path_parts) == 5:
                # Category level: year_1/term_1/block_1/anatomy/general
                year, term, block, subject, category = path_parts
                if (year in structure and 
                    term in structure[year]["terms"] and 
                    block in structure[year]["terms"][term]["blocks"] and
                    subject in structure[year]["terms"][term]["blocks"][block]["subjects"]):
                    structure[year]["terms"][term]["blocks"][block]["subjects"][subject]["categories"][category] = \
                        AutoNavigator._create_category_node(category, os.path.join(data_dir, year, term, block, subject, category))
        
        logger.info(f"✅ Built navigation structure with {len(structure)} years")
        return structure
    
    @staticmethod
    def _create_year_node(year: str, year_path: str) -> Dict:
        """Create year node"""
        display_name = AutoNavigator._format_display_name(year)
        return {
            "display_name": display_name,
            "terms": {}
        }
    
    @staticmethod
    def _create_term_node(term: str, term_path: str) -> Dict:
        """Create term node"""
        display_name = AutoNavigator._format_display_name(term)
        return {
            "display_name": display_name,
            "blocks": {}
        }
    
    @staticmethod
    def _create_block_node(block: str, block_path: str) -> Dict:
        """Create block node"""
        display_name = AutoNavigator._format_display_name(block)
        return {
            "display_name": display_name,
            "subjects": {}
        }
    
    @staticmethod
    def _create_subject_node(subject: str, subject_path: str) -> Dict:
        """Create subject node and scan for categories"""
        display_name = AutoNavigator._format_display_name(subject)
        categories = {}
        
        # Scan for categories (subdirectories)
        if os.path.exists(subject_path):
            for item in os.listdir(subject_path):
                item_path = os.path.join(subject_path, item)
                if os.path.isdir(item_path):
                    categories[item] = AutoNavigator._create_category_node(item, item_path)
        
        return {
            "display_name": display_name,
            "categories": categories
        }
    
    @staticmethod
    def _create_category_node(category: str, category_path: str) -> Dict:
        """Create category node and scan for CSV files"""
        display_name = AutoNavigator._format_display_name(category)
        subtopics = {}
        
        # Scan for CSV files
        if os.path.exists(category_path):
            csv_files = [f for f in os.listdir(category_path) if f.endswith('.csv')]
            csv_files.sort()  # Sort for consistent ordering
            
            for csv_file in csv_files:
                display_name_csv = AutoNavigator._create_subtopic_display_name(csv_file)
                subtopics[csv_file] = display_name_csv
        
        return {
            "display_name": display_name,
            "subtopics": subtopics
        }
    
    @staticmethod
    def _format_display_name(name: str) -> str:
        """Convert directory name to display name"""
        # Remove underscores and capitalize
        display = name.replace('_', ' ').title()
        
        # Add emojis for common items
        emoji_map = {
            'anatomy': '📊',
            'histology': '🔬', 
            'biochemistry': '🧪',
            'physiology': '❤️',
            'pathology': '🔍',
            'pharmacology': '💊',
            'year': '📅',
            'term': '📚',
            'block': '📦',
            'general': '📖',
            'midterm': '📝',
            'final': '🎯',
            'formative': '📚'
        }
        
        for key, emoji in emoji_map.items():
            if key in name.lower():
                # Don't add emoji if it's already a subject with emoji
                if not any(subj in name.lower() for subj in ['anatomy', 'histology', 'biochemistry', 'physiology', 'pathology', 'pharmacology']):
                    display = f"{emoji} {display}"
                break
        
        return display
    
    @staticmethod
    def _create_subtopic_display_name(filename: str) -> str:
        """Create display name from CSV filename"""
        # Remove .csv extension
        base_name = filename[:-4]
        
        # Handle numbered files: "01_Introduction to Anatomy" -> "1. Introduction to Anatomy"
        if '_' in base_name:
            number_part, name_part = base_name.split('_', 1)
            try:
                number = int(number_part)
                return f"{number}. {name_part}"
            except ValueError:
                return base_name.replace('_', ' ')
        
        return base_name.replace('_', ' ')
    
    @staticmethod
    def print_structure(structure: Dict, level: int = 0):
        """Print the navigation structure for debugging"""
        indent = "  " * level
        
        for year, year_data in structure.items():
            print(f"{indent}📅 {year_data['display_name']} ({year})")
            
            for term, term_data in year_data['terms'].items():
                print(f"{indent}  📚 {term_data['display_name']} ({term})")
                
                for block, block_data in term_data['blocks'].items():
                    print(f"{indent}    📦 {block_data['display_name']} ({block})")
                    
                    for subject, subject_data in block_data['subjects'].items():
                        print(f"{indent}      📖 {subject_data['display_name']} ({subject})")
                        
                        for category, category_data in subject_data['categories'].items():
                            print(f"{indent}        🗂️ {category_data['display_name']} ({category}) - {len(category_data['subtopics'])} quizzes")
                            
                            for subtopic, display_name in category_data['subtopics'].items():
                                print(f"{indent}          📄 {display_name}")