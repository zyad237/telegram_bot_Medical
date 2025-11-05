# [file name]: config.py
"""
Configuration for medical curriculum structure
"""
import os

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    print("❌ ERROR: TELEGRAM_BOT_TOKEN environment variable not set!")
    exit(1)

CONFIG = {
    "data_dir": "data",
    "database_file": "quiz_bot.db",
    "max_questions_per_quiz": 150,
    "time_between_questions": 1,
}

# Start with empty structure - will be populated by auto_navigator
NAVIGATION_STRUCTURE = {}