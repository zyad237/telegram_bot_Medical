"""
Configuration and constants with manual display names
"""
import os

# Get token from environment variable
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    print("❌ ERROR: TELEGRAM_BOT_TOKEN environment variable not set!")
    exit(1)

CONFIG = {
    "data_dir": "data",
    "database_file": "quiz_bot.db",
    "max_questions_per_quiz": 50,
    "time_between_questions": 1,
}

# Manual display names for topics and subtopics
# The keys must match your folder names and CSV filenames EXACTLY
TOPIC_DISPLAY_NAMES = {
    "anatomy": "📊 Anatomy",  # Folder name is "anatomy" (lowercase)
    "histology": "🔬 Histology",  # Folder name is "histology" (lowercase)
}

SUBPROJECT_DISPLAY_NAMES = {
    "anatomy": {  # Must match folder name "anatomy"
        "3Rd_Month_To_Placenta": "3rd Month to placenta",           
        "Derivative_Of_Endoderm": "Derivative of Endoderm",  # Must match filename "Derivative_of_endoderm.csv"  
        "Derivatives_Of_The_Mesodermal": "Derivatives of the Mesodermal", 
        "The_Embryonic_Period_3Rd_To_8Th_Week": "The Embryonic Period 3rd to 8th Week",       
    },
    "histology": {  # Must match folder name "histology"
        # Add your histology CSV files here when you have them
    },
}