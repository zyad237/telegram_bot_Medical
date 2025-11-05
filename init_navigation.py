# [file name]: init_navigation.py (UPDATED)
"""
Initialize navigation structure at startup - FIXED VERSION
"""
import os
import logging
from config import CONFIG

logger = logging.getLogger(__name__)

def populate_csv_files(navigation_structure):
    """Populate CSV files into navigation structure - FIXED VERSION"""
    data_dir = CONFIG["data_dir"]
    csv_files_found = 0
    
    print("🔄 Populating CSV files into navigation structure...")
    
    for year, year_data in navigation_structure.items():
        for term, term_data in year_data["terms"].items():
            for block, block_data in term_data["blocks"].items():
                for subject, subject_data in block_data["subjects"].items():
                    for category, category_data in subject_data["categories"].items():
                        # Build the expected path
                        category_path = os.path.join(data_dir, year, term, block, subject, category)
                        
                        print(f"🔍 Checking: {category_path}")
                        
                        if os.path.exists(category_path):
                            # Find all CSV files in this category
                            csv_files = [f for f in os.listdir(category_path) if f.endswith('.csv')]
                            csv_files.sort()
                            
                            print(f"   Found {len(csv_files)} CSV files")
                            
                            # Clear existing subtopics and repopulate
                            category_data["subtopics"] = {}
                            
                            for csv_file in csv_files:
                                # Create display name
                                base_name = csv_file[:-4]  # Remove .csv
                                if '_' in base_name:
                                    try:
                                        number_part, name_part = base_name.split('_', 1)
                                        number = int(number_part)
                                        display_name = f"{number}. {name_part}"
                                    except ValueError:
                                        display_name = base_name.replace('_', ' ')
                                else:
                                    display_name = base_name.replace('_', ' ')
                                
                                category_data["subtopics"][csv_file] = display_name
                                csv_files_found += 1
                                print(f"   ✅ Added: {csv_file} -> {display_name}")
                        else:
                            print(f"   ❌ Directory not found: {category_path}")
    
    print(f"✅ Populated {csv_files_found} CSV files into navigation structure")
    return csv_files_found

def build_navigation_structure():
    """Build navigation structure from directory - FIXED VERSION"""
    data_dir = CONFIG["data_dir"]
    
    if not os.path.exists(data_dir):
        logger.error(f"❌ Data directory not found: {data_dir}")
        return {}
    
    print("🏗️ Building navigation structure from data directory...")
    
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
        
        # Build structure based on directory depth
        if len(path_parts) == 1:
            # Year level: year_1
            year = path_parts[0]
            if year not in structure:
                structure[year] = {
                    "display_name": format_display_name(year),
                    "terms": {}
                }
                
        elif len(path_parts) == 2:
            # Term level: year_1/term_1
            year, term = path_parts
            if year in structure and term not in structure[year]["terms"]:
                structure[year]["terms"][term] = {
                    "display_name": format_display_name(term),
                    "blocks": {}
                }
                
        elif len(path_parts) == 3:
            # Block level: year_1/term_1/block_1
            year, term, block = path_parts
            if (year in structure and 
                term in structure[year]["terms"] and 
                block not in structure[year]["terms"][term]["blocks"]):
                structure[year]["terms"][term]["blocks"][block] = {
                    "display_name": format_display_name(block),
                    "subjects": {}
                }
                
        elif len(path_parts) == 4:
            # Subject level: year_1/term_1/block_1/anatomy
            year, term, block, subject = path_parts
            if (year in structure and 
                term in structure[year]["terms"] and 
                block in structure[year]["terms"][term]["blocks"] and
                subject not in structure[year]["terms"][term]["blocks"][block]["subjects"]):
                structure[year]["terms"][term]["blocks"][block]["subjects"][subject] = {
                    "display_name": format_display_name(subject),
                    "categories": {}
                }
                
        elif len(path_parts) == 5:
            # Category level: year_1/term_1/block_1/anatomy/midterm
            year, term, block, subject, category = path_parts
            if (year in structure and 
                term in structure[year]["terms"] and 
                block in structure[year]["terms"][term]["blocks"] and
                subject in structure[year]["terms"][term]["blocks"][block]["subjects"] and
                category not in structure[year]["terms"][term]["blocks"][block]["subjects"][subject]["categories"]):
                structure[year]["terms"][term]["blocks"][block]["subjects"][subject]["categories"][category] = {
                    "display_name": format_display_name(category),
                    "subtopics": {}  # This will be populated with CSV files
                }
    
    # Now populate CSV files
    csv_count = populate_csv_files(structure)
    
    print(f"✅ Built navigation structure with {len(structure)} years and {csv_count} CSV files")
    return structure

def format_display_name(name: str) -> str:
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

def initialize_navigation():
    """Initialize the navigation structure and update config"""
    print("🔄 Building navigation structure from data directory...")
    
    # Build navigation structure
    NAVIGATION_STRUCTURE = build_navigation_structure()
    
    if NAVIGATION_STRUCTURE:
        print("✅ Navigation structure built successfully!")
        
        # Update the config module
        import config
        config.NAVIGATION_STRUCTURE = NAVIGATION_STRUCTURE
        
        # Print summary
        print("\n📊 NAVIGATION STRUCTURE SUMMARY:")
        for year, year_data in NAVIGATION_STRUCTURE.items():
            print(f"📅 {year_data['display_name']}")
            for term, term_data in year_data["terms"].items():
                print(f"  📚 {term_data['display_name']}")
                for block, block_data in term_data["blocks"].items():
                    print(f"    📦 {block_data['display_name']}")
                    for subject, subject_data in block_data["subjects"].items():
                        print(f"      📖 {subject_data['display_name']}")
                        for category, category_data in subject_data["categories"].items():
                            subtopic_count = len(category_data["subtopics"])
                            print(f"        🗂️ {category_data['display_name']} - {subtopic_count} quizzes")
        
        return True
    else:
        print("❌ Failed to build navigation structure!")
        return False

# Initialize when imported
NAVIGATION_STRUCTURE = {}
if initialize_navigation():
    from config import NAVIGATION_STRUCTURE as NAV_STRUCT
    NAVIGATION_STRUCTURE = NAV_STRUCT