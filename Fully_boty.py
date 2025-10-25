#!/usr/bin/env python3
"""
Telegram Quiz Bot - Railway Optimized Dynamic Version
Automatically creates and manages data structure on Railway.
"""

import os
import csv
import asyncio
import logging
import sqlite3
import json
import random
import re
import html
from datetime import datetime
from typing import Dict, List, Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    PollAnswerHandler,
)
from telegram.error import TelegramError, BadRequest

# ==============================
# CONFIGURATION
# ==============================

# Get token from environment variable
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    print("❌ ERROR: TELEGRAM_BOT_TOKEN environment variable not set!")
    print("Please set it in your deployment platform's environment variables")
    exit(1)

CONFIG = {
    "data_dir": "data",
    "database_file": "quiz_bot.db",
    "max_questions_per_quiz": 50,
    "time_between_questions": 2,
}

# Initialize logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('quiz_bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ==============================
# TEXT SANITIZATION
# ==============================

def sanitize_text(text: str) -> str:
    """Sanitize text to prevent Markdown parsing errors."""
    if not text:
        return ""
    
    text = html.escape(text)
    markdown_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in markdown_chars:
        text = text.replace(char, f'\\{char}')
    
    text = re.sub(r'\\+', r'\\', text)
    return text

# ==============================
# DYNAMIC DATA MANAGER - RAILWAY OPTIMIZED
# ==============================

class DataManager:
    """Manages dynamic data creation optimized for Railway deployment"""
    
    @staticmethod
    def ensure_data_structure():
        """Ensure data structure exists and create comprehensive sample data"""
        data_dir = CONFIG["data_dir"]
        
        # Always create data directory
        os.makedirs(data_dir, exist_ok=True)
        logger.info(f"📁 Ensured data directory exists: {data_dir}")
        
        # Create comprehensive sample data
        DataManager.create_comprehensive_sample_data()
        
        # Verify the structure was created
        topics = DataManager.get_existing_topics()
        if topics:
            logger.info(f"✅ Data structure verified. Topics: {topics}")
        else:
            logger.error("❌ Failed to create data structure")
    
    @staticmethod
    def get_existing_topics() -> List[str]:
        """Get list of existing topics"""
        data_dir = CONFIG["data_dir"]
        if not os.path.exists(data_dir):
            return []
        
        topics = [d for d in os.listdir(data_dir) 
                 if os.path.isdir(os.path.join(data_dir, d)) and not d.startswith('.')]
        return sorted(topics)
    
    @staticmethod
    def create_comprehensive_sample_data():
        """Create comprehensive sample data that will definitely work"""
        data_dir = CONFIG["data_dir"]
        
        # Comprehensive sample data covering multiple topics
        sample_data = {
            "ana": {
                "Human Body Basics.csv": [
                    ["What is the largest organ in the human body?", "Liver", "Skin", "Heart", "Lungs", "B"],
                    ["How many bones are in the adult human body?", "196", "206", "216", "226", "B"],
                    ["What carries oxygen in the blood?", "Platelets", "White blood cells", "Red blood cells", "Plasma", "C"],
                    ["What is the normal human body temperature?", "36.5°C", "37.0°C", "37.5°C", "38.0°C", "B"],
                    ["Which organ produces insulin?", "Liver", "Pancreas", "Kidney", "Stomach", "B"]
                ],
                "Organ Systems.csv": [
                    ["Which system includes the heart and blood vessels?", "Nervous", "Circulatory", "Digestive", "Respiratory", "B"],
                    ["What is the main function of the respiratory system?", "Blood circulation", "Oxygen exchange", "Food digestion", "Waste removal", "B"],
                    ["Which system is responsible for movement?", "Nervous", "Circulatory", "Muscular", "Endocrine", "C"]
                ]
            },
            "biology": {
                "Cell Biology.csv": [
                    ["What is the powerhouse of the cell?", "Nucleus", "Mitochondria", "Ribosome", "Golgi apparatus", "B"],
                    ["What process do plants use to make food?", "Respiration", "Photosynthesis", "Digestion", "Fermentation", "B"],
                    ["What is the basic unit of life?", "Atom", "Cell", "Molecule", "Organ", "B"]
                ],
                "Genetics.csv": [
                    ["How many chromosomes do humans have?", "23", "46", "52", "64", "B"],
                    ["What is DNA's main function?", "Energy production", "Genetic information storage", "Cell structure", "Waste removal", "B"]
                ]
            },
            "science": {
                "Physics Basics.csv": [
                    ["What is the unit of force?", "Joule", "Watt", "Newton", "Volt", "C"],
                    ["What is the speed of light?", "300,000 km/s", "150,000 km/s", "500,000 km/s", "1,000,000 km/s", "A"]
                ],
                "Chemistry.csv": [
                    ["What is the chemical symbol for gold?", "Go", "Gd", "Au", "Ag", "C"],
                    ["What is H2O commonly known as?", "Oxygen", "Hydrogen", "Water", "Carbon dioxide", "C"]
                ]
            },
            "general_knowledge": {
                "World Geography.csv": [
                    ["What is the largest continent?", "Africa", "Europe", "Asia", "North America", "C"],
                    ["What is the capital of France?", "London", "Paris", "Berlin", "Madrid", "B"]
                ],
                "History.csv": [
                    ["Who was the first president of the United States?", "Thomas Jefferson", "George Washington", "Abraham Lincoln", "John Adams", "B"]
                ]
            }
        }
        
        files_created = 0
        for topic, subtopics in sample_data.items():
            topic_dir = os.path.join(data_dir, topic)
            os.makedirs(topic_dir, exist_ok=True)
            
            for filename, questions in subtopics.items():
                file_path = os.path.join(topic_dir, filename)
                
                # Always create/overwrite to ensure files exist
                try:
                    with open(file_path, 'w', encoding='utf-8', newline='') as f:
                        writer = csv.writer(f)
                        for question_data in questions:
                            writer.writerow(question_data)
                    
                    files_created += 1
                    logger.info(f"📄 Created sample file: {topic}/{filename}")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to create {file_path}: {e}")
        
        logger.info(f"✅ Created {files_created} sample files across {len(sample_data)} topics")
        return files_created
    
    @staticmethod
    def scan_for_new_files():
        """Scan for any new CSV files that were added manually"""
        data_dir = CONFIG["data_dir"]
        if not os.path.exists(data_dir):
            return False
        
        total_files = 0
        for topic in os.listdir(data_dir):
            topic_path = os.path.join(data_dir, topic)
            if os.path.isdir(topic_path):
                csv_files = [f for f in os.listdir(topic_path) if f.endswith('.csv')]
                total_files += len(csv_files)
                if csv_files:
                    logger.info(f"📁 {topic}: {len(csv_files)} CSV files")
        
        logger.info(f"🔍 File scan complete: {total_files} total CSV files")
        return total_files > 0

# ==============================
# CALLBACK DATA MANAGER
# ==============================

class CallbackManager:
    """Manage callback data to work with actual filenames"""
    
    MAX_CALLBACK_LENGTH = 64
    
    @staticmethod
    def sanitize_callback_text(text: str) -> str:
        """Sanitize text for safe callback data"""
        sanitized = re.sub(r'[^\w\s-]', '', text)
        sanitized = re.sub(r'[-\s]+', '_', sanitized)
        return sanitized.lower()[:20]
    
    @staticmethod
    def create_topic_callback(topic: str) -> str:
        """Create safe topic callback data"""
        safe_topic = CallbackManager.sanitize_callback_text(topic)
        return f"t:{safe_topic}"
    
    @staticmethod
    def create_subtopic_callback(topic: str, subtopic: str) -> str:
        """Create safe subtopic callback data using actual subtopic name"""
        safe_topic = CallbackManager.sanitize_callback_text(topic)
        return f"s:{safe_topic}:{subtopic}"[:CallbackManager.MAX_CALLBACK_LENGTH]
    
    @staticmethod
    def parse_callback_data(callback_data: str) -> Optional[Dict]:
        """Parse callback data safely"""
        try:
            if callback_data == "main_menu":
                return {"type": "main_menu"}
            elif callback_data.startswith("t:"):
                return {"type": "topic", "topic": callback_data[2:]}
            elif callback_data.startswith("s:"):
                parts = callback_data.split(":", 2)
                if len(parts) >= 3:
                    return {"type": "subtopic", "topic": parts[1], "subtopic": parts[2]}
        except Exception as e:
            logger.error(f"Error parsing callback data: {e}")
        return None

# ==============================
# DATABASE MANAGEMENT
# ==============================

class DatabaseManager:
    def __init__(self, db_file: str):
        self.db_file = db_file
        self.init_database()
    
    def init_database(self):
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        first_name TEXT,
                        last_name TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_progress (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        topic TEXT NOT NULL,
                        subtopic TEXT NOT NULL,
                        score INTEGER DEFAULT 0,
                        total_questions INTEGER DEFAULT 0,
                        completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')
                conn.commit()
                logger.info("✅ Database initialized successfully")
        except sqlite3.Error as e:
            logger.error(f"❌ Database error: {e}")
    
    def update_user(self, user_id: int, username: str, first_name: str, last_name: str):
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO users 
                    (user_id, username, first_name, last_name)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, username, first_name, last_name))
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error updating user {user_id}: {e}")
    
    def save_user_progress(self, user_id: int, topic: str, subtopic: str, score: int, total_questions: int):
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO user_progress 
                    (user_id, topic, subtopic, score, total_questions)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, topic, subtopic, score, total_questions))
                conn.commit()
                logger.info(f"💾 Saved progress for user {user_id}: {score}/{total_questions}")
        except sqlite3.Error as e:
            logger.error(f"Error saving progress: {e}")
    
    def get_user_stats(self, user_id: int) -> Dict:
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM user_progress WHERE user_id = ?', (user_id,))
                total_quizzes = cursor.fetchone()[0] or 0
                
                cursor.execute('''
                    SELECT AVG(score * 100.0 / total_questions) 
                    FROM user_progress WHERE user_id = ? AND total_questions > 0
                ''', (user_id,))
                avg_score = cursor.fetchone()[0] or 0
                
                return {
                    'total_quizzes': total_quizzes,
                    'average_score': round(avg_score, 1)
                }
        except sqlite3.Error as e:
            logger.error(f"Error getting stats: {e}")
            return {'total_quizzes': 0, 'average_score': 0}

# Initialize database
db = DatabaseManager(CONFIG["database_file"])

# ==============================
# QUIZ MANAGEMENT
# ==============================

class QuizManager:
    @staticmethod
    def shuffle_choices(question_data: Dict) -> Dict:
        """Shuffle answer choices while tracking correct answer"""
        original_options = question_data["options"]
        original_correct_index = question_data["correct_index"]
        
        indexed_options = list(enumerate(original_options))
        random.shuffle(indexed_options)
        
        shuffled_options = []
        new_correct_index = None
        
        for new_index, (original_index, option) in enumerate(indexed_options):
            shuffled_options.append(option)
            if original_index == original_correct_index:
                new_correct_index = new_index
        
        shuffled_question = question_data.copy()
        shuffled_question["options"] = shuffled_options
        shuffled_question["correct_index"] = new_correct_index
        shuffled_question["shuffled_correct_letter"] = ['A', 'B', 'C', 'D'][new_correct_index]
        
        return shuffled_question

class FileManager:
    @staticmethod
    def list_topics() -> List[str]:
        """Dynamically list all available topics"""
        return DataManager.get_existing_topics()
    
    @staticmethod
    def list_subtopics(topic: str) -> List[str]:
        """Dynamically list all available subtopics for a topic"""
        topic_path = os.path.join(CONFIG["data_dir"], topic)
        
        logger.info(f"🔍 Looking for subtopics in: {topic_path}")
        
        if not os.path.exists(topic_path):
            logger.warning(f"❌ Topic path does not exist: {topic_path}")
            # Try to create it
            os.makedirs(topic_path, exist_ok=True)
            logger.info(f"📁 Created topic directory: {topic_path}")
            return []
        
        # Get all CSV files and return their names without extension
        subtopics = []
        try:
            for file in os.listdir(topic_path):
                if file.endswith('.csv') and not file.startswith('.'):
                    # Return the filename without .csv extension
                    subtopic_name = file[:-4]
                    subtopics.append(subtopic_name)
        except Exception as e:
            logger.error(f"❌ Error listing subtopics for {topic}: {e}")
        
        logger.info(f"📚 Found {len(subtopics)} subtopics for {topic}: {subtopics}")
        return sorted(subtopics)
    
    @staticmethod
    def load_questions(topic: str, subtopic: str) -> List[Dict]:
        """Dynamically load questions from CSV file"""
        # Reconstruct the filename (subtopic is the filename without .csv)
        filename = f"{subtopic}.csv"
        file_path = os.path.join(CONFIG["data_dir"], topic, filename)
        
        logger.info(f"📖 Loading questions from: {file_path}")
        
        if not os.path.exists(file_path):
            logger.error(f"❌ Question file not found: {file_path}")
            # List available files for debugging
            topic_path = os.path.join(CONFIG["data_dir"], topic)
            if os.path.exists(topic_path):
                available_files = [f for f in os.listdir(topic_path) if f.endswith('.csv')]
                logger.info(f"📋 Available files in {topic}: {available_files}")
            
            return []
        
        questions = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                row_count = 0
                valid_questions = 0
                
                for i, row in enumerate(reader, 1):
                    row_count += 1
                    
                    # Skip empty rows, comments, and rows with insufficient data
                    if not row or not any(row) or row[0].startswith('#') or len(row) < 6:
                        continue
                    
                    # Clean and validate data
                    cleaned_row = [x.strip() for x in row[:6] if x.strip()]
                    if len(cleaned_row) < 6:
                        continue
                    
                    question, opt_a, opt_b, opt_c, opt_d, correct = cleaned_row
                    correct = correct.upper()
                    
                    # Validate correct answer format
                    if correct not in ['A', 'B', 'C', 'D']:
                        logger.warning(f"⚠️ Invalid correct answer in row {i}: '{correct}'")
                        continue
                    
                    # Sanitize all text
                    question = sanitize_text(question)
                    opt_a = sanitize_text(opt_a)
                    opt_b = sanitize_text(opt_b)
                    opt_c = sanitize_text(opt_c)
                    opt_d = sanitize_text(opt_d)
                    
                    questions.append({
                        "question": question,
                        "options": [opt_a, opt_b, opt_c, opt_d],
                        "correct": correct,
                        "correct_index": ord(correct) - ord('A')
                    })
                    valid_questions += 1
            
            logger.info(f"✅ Loaded {valid_questions} valid questions from {row_count} rows in {topic}/{subtopic}")
            
            if valid_questions == 0:
                logger.warning(f"⚠️ No valid questions found in {file_path}")
                
        except Exception as e:
            logger.error(f"❌ Error loading questions from {file_path}: {e}")
        
        return questions

# ==============================
# ERROR HANDLER
# ==============================

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    error = context.error
    logger.error(f"🚨 Exception while handling an update: {error}", exc_info=error)
    
    if isinstance(error, BadRequest):
        error_msg = str(error).lower()
        if any(msg in error_msg for msg in ["query is too old", "button_data_invalid", "message is not modified"]):
            logger.warning("⚠️ Ignoring common Telegram error")
            return
    
    try:
        if update and update.effective_chat:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ An error occurred. Please use /start to begin again.",
                parse_mode=None
            )
    except Exception as e:
        logger.error(f"❌ Could not send error message: {e}")

# ==============================
# BOT HANDLERS (Same as before, but optimized)
# ==============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    db.update_user(user.id, user.username, user.first_name, user.last_name)
    
    context.user_data.clear()
    
    topics = FileManager.list_topics()
    if not topics:
        await update.message.reply_text(
            "📝 No quiz topics available.\n\n"
            "The bot is creating sample data automatically...\n"
            "Please wait a moment and try /start again."
        )
        # Force create data structure
        DataManager.ensure_data_structure()
        return
    
    keyboard = []
    for topic in topics:
        callback_data = CallbackManager.create_topic_callback(topic)
        keyboard.append([InlineKeyboardButton(topic.title(), callback_data=callback_data)])
    
    # Add refresh button
    keyboard.append([InlineKeyboardButton("🔄 Refresh Topics", callback_data="refresh_topics")])
    
    await update.message.reply_text(
        "🎯 Welcome to Dynamic Quiz Bot!\n\n"
        "📚 Auto-detected topics and quizzes\n"
        "🔄 Dynamic file discovery\n"
        "⏰ No time limits\n\n"
        "Select a subject to begin:",
        parse_mode=None,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = (
        "🤖 Dynamic Quiz Bot Help\n\n"
        "📚 Commands:\n"
        "• /start - Start bot & see topics\n"
        "• /stats - Your statistics\n"
        "• /refresh - Refresh topics\n"
        "• /cancel - Cancel quiz\n"
        "• /help - This message\n\n"
        "🔄 The bot automatically detects\nnew CSV files in the data folder!"
    )
    
    await update.message.reply_text(help_text, parse_mode=None)

async def refresh_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manual refresh of available topics"""
    DataManager.scan_for_new_files()
    topics = FileManager.list_topics()
    
    if topics:
        await update.message.reply_text(
            f"✅ Refreshed! Found {len(topics)} topics.\nUse /start to see them.",
            parse_mode=None
        )
    else:
        await update.message.reply_text(
            "🔄 No topics found. Creating sample data...",
            parse_mode=None
        )
        DataManager.ensure_data_structure()

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats command"""
    user = update.effective_user
    stats = db.get_user_stats(user.id)
    
    if stats['total_quizzes'] == 0:
        await update.message.reply_text(
            "📊 You haven't completed any quizzes yet.\n"
            "Use /start to begin your first quiz!"
        )
        return
    
    stats_text = (
        f"📊 Your Quiz Statistics\n\n"
        f"• Total Quizzes: {stats['total_quizzes']}\n"
        f"• Average Score: {stats['average_score']}%\n\n"
        f"Keep up the great work! 🎯"
    )
    
    await update.message.reply_text(stats_text, parse_mode=None)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all callback queries"""
    query = update.callback_query
    
    try:
        await query.answer()
    except BadRequest:
        pass
    
    callback_data = query.data
    logger.info(f"🔄 Received callback: {callback_data}")
    
    try:
        if callback_data == "refresh_topics":
            await handle_refresh_topics(update, context)
            return
        
        parsed = CallbackManager.parse_callback_data(callback_data)
        if not parsed:
            await query.edit_message_text("❌ Invalid selection. Use /start to begin again.", parse_mode=None)
            return
        
        if parsed["type"] == "main_menu":
            await handle_main_menu(update, context)
        elif parsed["type"] == "topic":
            await handle_topic_selection(update, context, parsed["topic"])
        elif parsed["type"] == "subtopic":
            await handle_subtopic_selection(update, context, parsed["topic"], parsed["subtopic"])
                
    except Exception as e:
        logger.error(f"❌ Error handling callback: {e}")
        await query.edit_message_text("❌ An error occurred. Please try again.", parse_mode=None)

async def handle_refresh_topics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle topic refresh"""
    query = update.callback_query
    DataManager.scan_for_new_files()
    await handle_main_menu(update, context)

async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle return to main menu"""
    query = update.callback_query
    topics = FileManager.list_topics()
    
    if not topics:
        await query.edit_message_text(
            "🔄 No topics found. Creating sample data...",
            parse_mode=None
        )
        DataManager.ensure_data_structure()
        topics = FileManager.list_topics()
    
    keyboard = []
    for topic in topics:
        callback_data = CallbackManager.create_topic_callback(topic)
        keyboard.append([InlineKeyboardButton(topic.title(), callback_data=callback_data)])
    
    keyboard.append([InlineKeyboardButton("🔄 Refresh Topics", callback_data="refresh_topics")])
    
    try:
        await query.edit_message_text(
            "📚 Select a subject:",
            parse_mode=None,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except BadRequest as e:
        if "message is not modified" not in str(e).lower():
            raise e

async def handle_topic_selection(update: Update, context: ContextTypes.DEFAULT_TYPE, topic: str):
    """Handle topic selection"""
    query = update.callback_query
    subtopics = FileManager.list_subtopics(topic)
    
    if not subtopics:
        await query.edit_message_text(f"❌ No quizzes available for {topic}", parse_mode=None)
        return
    
    keyboard = []
    for subtopic in subtopics:
        callback_data = CallbackManager.create_subtopic_callback(topic, subtopic)
        keyboard.append([InlineKeyboardButton(subtopic, callback_data=callback_data)])
    
    keyboard.append([InlineKeyboardButton("« Back to Subjects", callback_data="main_menu")])
    
    try:
        await query.edit_message_text(
            f"🧩 {topic.title()} - Choose a topic:",
            parse_mode=None,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except BadRequest as e:
        if "message is not modified" not in str(e).lower():
            raise e

async def handle_subtopic_selection(update: Update, context: ContextTypes.DEFAULT_TYPE, topic: str, subtopic: str):
    """Handle subtopic selection and start quiz"""
    query = update.callback_query
    
    logger.info(f"🚀 Starting quiz: {topic}/{subtopic}")
    questions = FileManager.load_questions(topic, subtopic)
    
    if not questions:
        await query.edit_message_text(
            f"❌ No questions found for {topic.title()} - {subtopic}\n\n"
            f"The bot will work with any CSV file in:\n"
            f"data/{topic}/your_file.csv\n\n"
            f"Format: question,optionA,optionB,optionC,optionD,correct",
            parse_mode=None
        )
        return
    
    if len(questions) > CONFIG["max_questions_per_quiz"]:
        questions = questions[:CONFIG["max_questions_per_quiz"]]
    
    context.user_data.update({
        "quiz_active": True,
        "questions": questions,
        "current_question": 0,
        "correct_answers": 0,
        "topic": topic,
        "subtopic": subtopic,
        "chat_id": query.message.chat_id,
    })
    
    await query.edit_message_text(
        f"🎯 Starting {topic.title()} - {subtopic} quiz!\n\n"
        f"• Questions: {len(questions)}\n"
        f"• Choices are shuffled\n"
        f"• No time limits\n\n"
        f"Good luck! 🍀",
        parse_mode=None
    )
    
    await asyncio.sleep(2)
    await send_next_question(update, context)

# ... [Keep the rest of the functions exactly the same: send_next_question, handle_poll_answer, finish_quiz, cancel_command] ...

async def send_next_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send the next question in the quiz"""
    user_data = context.user_data
    
    if not user_data.get("quiz_active"):
        return
    
    current_index = user_data["current_question"]
    questions = user_data["questions"]
    chat_id = user_data["chat_id"]
    
    if current_index >= len(questions):
        await finish_quiz(update, context)
        return
    
    original_question = questions[current_index]
    shuffled_question = QuizManager.shuffle_choices(original_question)
    user_data["current_shuffled"] = shuffled_question
    
    progress = f"Question {current_index + 1}/{len(questions)}\n\n"
    question_text = progress + shuffled_question["question"]
    
    try:
        message = await context.bot.send_poll(
            chat_id=chat_id,
            question=question_text,
            options=shuffled_question["options"],
            type="quiz",
            correct_option_id=shuffled_question["correct_index"],
            is_anonymous=False,
        )
        
        user_data["active_poll_id"] = message.poll.id
        user_data["poll_message_id"] = message.message_id
        
        logger.info(f"📤 Sent question {current_index + 1} to user {chat_id}")
        
    except Exception as e:
        logger.error(f"❌ Error sending question {current_index + 1}: {e}")
        user_data["current_question"] += 1
        await asyncio.sleep(2)
        await send_next_question(update, context)

async def handle_poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle poll answers"""
    poll_answer = update.poll_answer
    user_data = context.user_data
    
    if user_data.get("active_poll_id") != poll_answer.poll_id:
        return
    
    if not user_data.get("quiz_active"):
        return
    
    shuffled_question = user_data.get("current_shuffled")
    if not shuffled_question:
        return
    
    user_answer = poll_answer.option_ids[0] if poll_answer.option_ids else None
    is_correct = user_answer == shuffled_question["correct_index"]
    
    if is_correct:
        user_data["correct_answers"] += 1
        feedback = "✅ Correct! Well done!"
    else:
        correct_letter = shuffled_question["shuffled_correct_letter"]
        feedback = f"❌ Incorrect. The correct answer was {correct_letter}"
    
    try:
        await context.bot.send_message(
            chat_id=user_data["chat_id"],
            text=feedback,
            reply_to_message_id=user_data.get("poll_message_id")
        )
    except Exception as e:
        logger.error(f"❌ Error sending feedback: {e}")
    
    try:
        await context.bot.stop_poll(
            chat_id=user_data["chat_id"],
            message_id=user_data.get("poll_message_id")
        )
    except Exception as e:
        logger.warning(f"⚠️ Could not stop poll: {e}")
    
    user_data["current_question"] += 1
    user_data["active_poll_id"] = None
    user_data["poll_message_id"] = None
    
    if "current_shuffled" in user_data:
        del user_data["current_shuffled"]
    
    await asyncio.sleep(CONFIG["time_between_questions"])
    await send_next_question(update, context)

async def finish_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Finish the quiz and show results"""
    user_data = context.user_data
    user = update.effective_user
    
    if not user_data.get("quiz_active"):
        return
    
    correct = user_data["correct_answers"]
    total = len(user_data["questions"])
    percentage = (correct / total) * 100 if total > 0 else 0
    
    if percentage >= 90:
        performance = "🎉 Outstanding! You're a quiz master! 🏆"
    elif percentage >= 75:
        performance = "👍 Great job! You know your stuff! ⭐"
    elif percentage >= 60:
        performance = "😊 Good work! Keep practicing! ✨"
    else:
        performance = "📚 Keep studying! You'll get better! 💪"
    
    db.save_user_progress(
        user_id=user.id,
        topic=user_data["topic"],
        subtopic=user_data["subtopic"],
        score=correct,
        total_questions=total
    )
    
    results_text = (
        f"🎯 Quiz Completed!\n\n"
        f"{performance}\n\n"
        f"📊 Final Score: {correct}/{total} ({percentage:.1f}%)\n"
        f"📚 Topic: {user_data['topic'].title()}\n"
        f"🧩 Subtopic: {user_data['subtopic']}\n\n"
        f"Use /start to try another quiz!"
    )
    
    await context.bot.send_message(
        chat_id=user_data["chat_id"],
        text=results_text,
        parse_mode=None
    )
    
    user_data.clear()
    logger.info(f"✅ Quiz completed for user {user.id}: {correct}/{total} ({percentage:.1f}%)")

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /cancel command"""
    user_data = context.user_data
    
    if user_data.get("quiz_active"):
        try:
            if user_data.get("active_poll_id"):
                await context.bot.stop_poll(
                    chat_id=user_data["chat_id"],
                    message_id=user_data.get("poll_message_id")
                )
        except Exception as e:
            logger.warning(f"⚠️ Could not stop poll during cancel: {e}")
        
        user_data.clear()
        await update.message.reply_text("❌ Quiz cancelled. Use /start to begin a new one.")
    else:
        await update.message.reply_text("ℹ️ No active quiz to cancel.")

# ==============================
# MAIN FUNCTION - RAILWAY OPTIMIZED
# ==============================

def main():
    """Start the bot - Railway optimized"""
    if not TOKEN:
        logger.error("❌ No bot token provided. Set TELEGRAM_BOT_TOKEN environment variable.")
        return
    
    # Force initialize data structure before anything else
    logger.info("🚀 Initializing Railway-optimized bot...")
    logger.info("📁 Creating data structure...")
    DataManager.ensure_data_structure()
    
    try:
        application = Application.builder().token(TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("stats", stats_command))
        application.add_handler(CommandHandler("refresh", refresh_command))
        application.add_handler(CommandHandler("cancel", cancel_command))
        application.add_handler(CallbackQueryHandler(handle_callback))
        application.add_handler(PollAnswerHandler(handle_poll_answer))
        
        application.add_error_handler(error_handler)
        
        # Start the bot with comprehensive logging
        logger.info("🤖 Dynamic Quiz Bot is starting on Railway...")
        logger.info("✅ Token loaded from environment variable")
        
        topics = FileManager.list_topics()
        if topics:
            logger.info(f"📚 Available topics: {', '.join(topics)}")
            for topic in topics:
                subtopics = FileManager.list_subtopics(topic)
                if subtopics:
                    logger.info(f"   📂 {topic}: {len(subtopics)} subtopics")
                else:
                    logger.warning(f"   ⚠️ {topic}: No subtopics found")
        else:
            logger.error("❌ CRITICAL: No topics found after initialization!")
        
        logger.info("🔄 Starting bot polling...")
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            poll_interval=1,
            timeout=30,
            drop_pending_updates=True
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")
        print(f"❌ Bot failed to start: {e}")

if __name__ == "__main__":
    main()