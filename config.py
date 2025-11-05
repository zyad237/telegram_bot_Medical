# [file name]: config.py (UPDATED)
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
    "max_questions_per_quiz": 100,
    "time_between_questions": 1.5,
}

# Navigation structure will be populated by init_navigation
NAVIGATION_STRUCTURE = {}