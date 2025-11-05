# [file name]: init_navigation.py
"""
Initialize navigation structure at startup - FIXED
"""
import os
import logging
from config import CONFIG

logger = logging.getLogger(__name__)

def initialize_navigation():
    """Initialize the navigation structure - FIXED VERSION"""
    print("🔄 Building navigation structure...")
    
    # Build the structure manually
    NAVIGATION_STRUCTURE = {
        "year_1": {
            "display_name": "📅 Year 1",
            "terms": {
                "term_1": {
                    "display_name": "📚 Semester 1", 
                    "blocks": {
                        "block_1": {
                            "display_name": "📦 Block 1 (PMS)",
                            "subjects": {
                                "anatomy": {
                                    "display_name": "📊 Anatomy",
                                    "categories": {
                                        "general": {
                                            "display_name": "📖 General Anatomy", 
                                            "subtopics": {}
                                        },
                                        "midterm": {
                                            "display_name": "📝 Midterm Exams",
                                            "subtopics": {}
                                        },
                                        "final": {
                                            "display_name": "🎯 Final Exams",
                                            "subtopics": {}
                                        },
                                        "formative": {
                                            "display_name": "📚 Formative Assessments",
                                            "subtopics": {}
                                        }
                                    }
                                },
                                "histology": {
                                    "display_name": "🔬 Histology",
                                    "categories": {
                                        "general": {
                                            "display_name": "📖 General Histology",
                                            "subtopics": {}
                                        },
                                        "midterm": {
                                            "display_name": "📝 Midterm Exams", 
                                            "subtopics": {}
                                        },
                                        "final": {
                                            "display_name": "🎯 Final Exams",
                                            "subtopics": {}
                                        },
                                        "formative": {
                                            "display_name": "📚 Formative Assessments",
                                            "subtopics": {}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    # Scan and populate CSV files for ALL categories
    csv_total = 0
    for year in ["year_1"]:
        for term in ["term_1"]:
            for block in ["block_1"]:
                for subject in ["anatomy", "histology"]:
                    for category in ["general", "midterm", "final", "formative"]:
                        category_path = os.path.join(CONFIG["data_dir"], year, term, block, subject, category)
                        
                        if os.path.exists(category_path):
                            csv_files = [f for f in os.listdir(category_path) if f.endswith('.csv')]
                            csv_files.sort()
                            
                            for csv_file in csv_files:
                                # Create display name
                                base_name = csv_file[:-4]
                                if '_' in base_name:
                                    try:
                                        num_part, name_part = base_name.split('_', 1)
                                        num = int(num_part)
                                        display_name = f"{num}. {name_part}"
                                    except ValueError:
                                        display_name = base_name.replace('_', ' ')
                                else:
                                    display_name = base_name.replace('_', ' ')
                                
                                NAVIGATION_STRUCTURE[year]["terms"][term]["blocks"][block]["subjects"][subject]["categories"][category]["subtopics"][csv_file] = display_name
                                csv_total += 1
                            
                            print(f"✅ {subject}/{category}: {len(csv_files)} CSV files")
                        else:
                            print(f"⚠️  Path not found: {category_path}")
    
    print(f"🎯 Total CSV files loaded: {csv_total}")
    
    # Update config
    import config
    config.NAVIGATION_STRUCTURE = NAVIGATION_STRUCTURE
    
    return True

# Initialize immediately
NAVIGATION_STRUCTURE = {}
if initialize_navigation():
    from config import NAVIGATION_STRUCTURE as NAV_STRUCT
    NAVIGATION_STRUCTURE = NAV_STRUCT
    print("✅ Navigation structure initialized successfully!")
else:
    print("❌ Navigation structure initialization failed!")