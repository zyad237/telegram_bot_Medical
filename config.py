# [file name]: config.py
"""
Configuration for medical curriculum structure
"""
import os
import logging

logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    print("❌ ERROR: TELEGRAM_BOT_TOKEN environment variable not set!")
    exit(1)

CONFIG = {
    "data_dir": "data",
    "database_file": "quiz_bot.db",
    "max_questions_per_quiz": 50,
    "time_between_questions": 1.5,
}

# MANUAL navigation structure that matches your exact directory structure
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

def populate_csv_files():
    """Automatically find and populate CSV files in the navigation structure"""
    data_dir = CONFIG["data_dir"]
    csv_files_found = 0
    
    print("🔄 Populating CSV files into navigation structure...")
    
    for year in NAVIGATION_STRUCTURE.keys():
        for term in NAVIGATION_STRUCTURE[year]["terms"].keys():
            for block in NAVIGATION_STRUCTURE[year]["terms"][term]["blocks"].keys():
                for subject in NAVIGATION_STRUCTURE[year]["terms"][term]["blocks"][block]["subjects"].keys():
                    for category in NAVIGATION_STRUCTURE[year]["terms"][term]["blocks"][block]["subjects"][subject]["categories"].keys():
                        # Build the expected path
                        category_path = os.path.join(data_dir, year, term, block, subject, category)
                        
                        print(f"🔍 Checking: {category_path}")
                        
                        if os.path.exists(category_path):
                            # Find all CSV files in this category
                            csv_files = [f for f in os.listdir(category_path) if f.endswith('.csv')]
                            csv_files.sort()
                            
                            print(f"   Found {len(csv_files)} CSV files")
                            
                            for csv_file in csv_files:
                                # Create display name
                                base_name = csv_file[:-4]  # Remove .csv
                                if '_' in base_name:
                                    number_part, name_part = base_name.split('_', 1)
                                    try:
                                        number = int(number_part)
                                        display_name = f"{number}. {name_part}"
                                    except ValueError:
                                        display_name = base_name.replace('_', ' ')
                                else:
                                    display_name = base_name.replace('_', ' ')
                                
                                NAVIGATION_STRUCTURE[year]["terms"][term]["blocks"][block]["subjects"][subject]["categories"][category]["subtopics"][csv_file] = display_name
                                csv_files_found += 1
                                print(f"   ✅ Added: {csv_file} -> {display_name}")
                        else:
                            print(f"   ❌ Directory not found: {category_path}")
    
    print(f"✅ Populated {csv_files_found} CSV files into navigation structure")

# Populate the CSV files on startup
populate_csv_files()