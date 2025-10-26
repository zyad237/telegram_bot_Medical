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
    "database_file": "quiz_bot.db",  # Make sure this line exists
    "max_questions_per_quiz": 100,
    "time_between_questions": 1,
}

# Manual display names for topics and subtopics
# The keys must match your folder names and CSV filenames
TOPIC_DISPLAY_NAMES = {
    "anatomy": "📊 Anatomy",
    "histology": "🔬 Histology",
}

SUBPROJECT_DISPLAY_NAMES = {
    "anatomy": {
        "3rd_Month_to_placenta": "3rd Month to placenta",           
        "Derivative_of_endoderm": "Derivative of Endoderm",   
        "Derivatives_of_the_Mesodermal": "Derivatives of the Mesodermal", 
        "The_Embryonic_Period_3rd_to_8th_Week": "The Embryonic Period 3rd to 8th Week",       
    },
    "histology": {
        "enzymes": "Physics Principles",
    },
    
    }