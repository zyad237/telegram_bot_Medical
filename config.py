"""
Configuration and constants with nested structure
"""
import os

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    print("❌ ERROR: TELEGRAM_BOT_TOKEN environment variable not set!")
    exit(1)

CONFIG = {
    "data_dir": "data",
    "database_file": "quiz_bot.db",
    "max_questions_per_quiz": 100,
    "time_between_questions": 1,
}

# Nested structure: Topic -> Category -> Subtopic
TOPIC_DISPLAY_NAMES = {
    "anatomy": "📊 Anatomy",
    "histology": "🔬 Histology",
}

# Structure: topic -> category -> subtopic -> display_name
NESTED_STRUCTURE = {
    "anatomy": {
        "general": {
            "display_name": "General Anatomy",
            "subtopics": {
                "introduction": "Introduction to Anatomy",
                "terminology": "Anatomical Terminology",
                "tissues": "Basic Tissues",
            }
        },
        "embryology": {
            "display_name": "Embryology", 
            "subtopics": {
                "3rd_Month_to_placenta": "3rd Month to Placenta",
                "Derivatives_of_endoderm": "Derivative of Endoderm",
                "Derivatives_of_Mesodermal": "Derivatives of the Mesodermal",
                "The_Embryonic_Period_3rd_to_8th_Week": "The Embryonic Period 3rd to 8th Week",
            }
        }
    },
    "histology": {
        "general": {
            "display_name": "General Histology",
            "subtopics": {
                "Bones": "Bone Tissue",
            }
        }
    }
}