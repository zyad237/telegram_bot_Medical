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
    "math": "📊 Mathematics",  # Folder: data/math/
    "science": "🔬 Science",   # Folder: data/science/
    "history": "📜 History",   # Folder: data/history/
}

SUBPROJECT_DISPLAY_NAMES = {
    "math": {
        "algebra": "Algebra Basics",           # File: algebra.csv
        "geometry": "Geometry Fundamentals",   # File: geometry.csv
        "calculus": "Calculus Concepts",       # File: calculus.csv
    },
    "science": {
        "physics": "Physics Principles",       # File: physics.csv
        "chemistry": "Chemistry Essentials",   # File: chemistry.csv
        "biology": "Biology Basics",           # File: biology.csv
    },
    "history": {
        "ancient": "Ancient Civilizations",    # File: ancient.csv
        "world_war": "World Wars",             # File: world_war.csv
        "modern": "Modern History",            # File: modern.csv
    }
}