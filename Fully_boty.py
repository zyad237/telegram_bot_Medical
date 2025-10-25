#!/usr/bin/env python3
"""
Telegram Quiz Bot
A robust, production-ready quiz bot for Telegram that sends multiple-choice questions
from CSV files with shuffled answers and no time limits.

Author: Your Name
Version: 1.0.0
License: MIT
"""

import os
import csv
import asyncio
import logging
import sqlite3
import json
import random
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    PollAnswerHandler,
)
from telegram.error import TelegramError

# ==============================
# CONFIGURATION
# ==============================

# Bot configuration
CONFIG = {
    "token": os.getenv("TELEGRAM_BOT_TOKEN", ""),  # Set your bot token in environment
    "data_dir": "data",
    "database_file": "quiz_bot.db",
    "config_file": "bot_config.json",
    "admin_ids": [],  # Add admin user IDs for special commands
    "max_questions_per_quiz": 50,
    "time_between_questions": 2,
    "supported_languages": ["en", "es", "fr"],  # Add more as needed
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
# DATABASE MANAGEMENT
# ==============================

class DatabaseManager:
    """Manage SQLite database for user progress and bot state"""
    
    def __init__(self, db_file: str):
        self.db_file = db_file
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                # Users table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        first_name TEXT,
                        last_name TEXT,
                        language_code TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # User progress table
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
                
                # User settings table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_settings (
                        user_id INTEGER PRIMARY KEY,
                        current_topic TEXT,
                        current_subtopic TEXT,
                        language TEXT DEFAULT 'en',
                        notifications_enabled BOOLEAN DEFAULT 1,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')
                
                # Quiz sessions table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS quiz_sessions (
                        session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        topic TEXT NOT NULL,
                        subtopic TEXT NOT NULL,
                        current_question INTEGER DEFAULT 0,
                        correct_answers INTEGER DEFAULT 0,
                        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        completed BOOLEAN DEFAULT 0,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {e}")
    
    def update_user(self, user_id: int, username: str, first_name: str, last_name: str, language_code: str):
        """Update or create user record"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO users 
                    (user_id, username, first_name, last_name, language_code, last_active)
                    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (user_id, username, first_name, last_name, language_code))
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error updating user {user_id}: {e}")
    
    def save_user_progress(self, user_id: int, topic: str, subtopic: str, score: int, total_questions: int):
        """Save user quiz progress"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO user_progress 
                    (user_id, topic, subtopic, score, total_questions)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, topic, subtopic, score, total_questions))
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error saving progress for user {user_id}: {e}")
    
    def get_user_stats(self, user_id: int) -> Dict:
        """Get user statistics"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                # Total quizzes
                cursor.execute('''
                    SELECT COUNT(*) FROM user_progress WHERE user_id = ?
                ''', (user_id,))
                total_quizzes = cursor.fetchone()[0]
                
                # Average score
                cursor.execute('''
                    SELECT AVG(score * 100.0 / total_questions) 
                    FROM user_progress WHERE user_id = ? AND total_questions > 0
                ''', (user_id,))
                avg_score = cursor.fetchone()[0] or 0
                
                # Recent progress
                cursor.execute('''
                    SELECT topic, subtopic, score, total_questions, completed_at
                    FROM user_progress 
                    WHERE user_id = ? 
                    ORDER BY completed_at DESC 
                    LIMIT 5
                ''', (user_id,))
                recent_quizzes = cursor.fetchall()
                
                return {
                    'total_quizzes': total_quizzes,
                    'average_score': round(avg_score, 1),
                    'recent_quizzes': recent_quizzes
                }
                
        except sqlite3.Error as e:
            logger.error(f"Error getting stats for user {user_id}: {e}")
            return {}

# Initialize database
db = DatabaseManager(CONFIG["database_file"])

# ==============================
# QUIZ MANAGEMENT
# ==============================

class QuizManager:
    """Manage quiz questions and operations"""
    
    @staticmethod
    def shuffle_choices(question_data: Dict) -> Dict:
        """Shuffle answer choices while tracking correct answer"""
        original_options = question_data["options"]
        original_correct_index = question_data["correct_index"]
        
        # Create indexed options and shuffle
        indexed_options = list(enumerate(original_options))
        random.shuffle(indexed_options)
        
        # Find new correct index
        shuffled_options = []
        new_correct_index = None
        
        for new_index, (original_index, option) in enumerate(indexed_options):
            shuffled_options.append(option)
            if original_index == original_correct_index:
                new_correct_index = new_index
        
        # Update question data
        shuffled_question = question_data.copy()
        shuffled_question["options"] = shuffled_options
        shuffled_question["correct_index"] = new_correct_index
        shuffled_question["shuffled_correct_letter"] = ['A', 'B', 'C', 'D'][new_correct_index]
        
        return shuffled_question
    
    @staticmethod
    def validate_csv_format(file_path: str) -> bool:
        """Validate CSV file format"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for i, row in enumerate(reader, 1):
                    if not row or row[0].startswith('#'):
                        continue
                    if len(row) < 6:
                        logger.warning(f"Row {i} in {file_path} has insufficient columns")
                        return False
                    
                    # Validate correct answer format
                    correct_answer = row[5].strip().upper()
                    if correct_answer not in ['A', 'B', 'C', 'D']:
                        logger.warning(f"Invalid correct answer in row {i}: {correct_answer}")
                        return False
            return True
        except Exception as e:
            logger.error(f"Error validating CSV {file_path}: {e}")
            return False

class FileManager:
    """Manage quiz files and data"""
    
    @staticmethod
    def list_topics() -> List[str]:
        """List available topics"""
        data_dir = CONFIG["data_dir"]
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            logger.info(f"Created data directory: {data_dir}")
            return []
        
        topics = [d for d in os.listdir(data_dir) 
                 if os.path.isdir(os.path.join(data_dir, d)) and not d.startswith('.')]
        return sorted(topics)
    
    @staticmethod
    def list_subtopics(topic: str) -> List[str]:
        """List available subtopics for a topic"""
        topic_path = os.path.join(CONFIG["data_dir"], topic)
        if not os.path.exists(topic_path):
            return []
        
        subtopics = [f[:-4] for f in os.listdir(topic_path) 
                    if f.endswith('.csv') and not f.startswith('.')]
        return sorted(subtopics)
    
    @staticmethod
    def load_questions(topic: str, subtopic: str) -> List[Dict]:
        """Load questions from CSV file"""
        file_path = os.path.join(CONFIG["data_dir"], topic, f"{subtopic}.csv")
        
        if not os.path.exists(file_path):
            logger.error(f"Question file not found: {file_path}")
            return []
        
        if not QuizManager.validate_csv_format(file_path):
            logger.error(f"Invalid CSV format: {file_path}")
            return []
        
        questions = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for i, row in enumerate(reader, 1):
                    if not row or not any(row) or row[0].startswith('#'):
                        continue
                    
                    if len(row) < 6:
                        logger.warning(f"Skipping row {i}: insufficient columns")
                        continue
                    
                    # Clean and validate data
                    cleaned_row = [x.strip() for x in row[:6]]
                    question, opt_a, opt_b, opt_c, opt_d, correct = cleaned_row
                    correct = correct.upper()
                    
                    if correct not in ['A', 'B', 'C', 'D']:
                        logger.warning(f"Skipping row {i}: invalid correct answer '{correct}'")
                        continue
                    
                    questions.append({
                        "question": question,
                        "options": [opt_a, opt_b, opt_c, opt_d],
                        "correct": correct,
                        "correct_index": ord(correct) - ord('A')
                    })
            
            logger.info(f"Loaded {len(questions)} questions from {topic}/{subtopic}")
            return questions
            
        except Exception as e:
            logger.error(f"Error loading questions from {file_path}: {e}")
            return []

# ==============================
# BOT HANDLERS
# ==============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command"""
    user = update.effective_user
    db.update_user(user.id, user.username, user.first_name, user.last_name, user.language_code)
    
    # Clear any existing quiz state
    context.user_data.clear()
    
    topics = FileManager.list_topics()
    if not topics:
        await update.message.reply_text(
            "📝 No quiz topics available yet.\n\n"
            "To add quizzes, create folders in the 'data' directory with CSV files.\n"
            "Each CSV should have: question,optionA,optionB,optionC,optionD,correct_answer"
        )
        return
    
    keyboard = []
    for topic in topics:
        keyboard.append([InlineKeyboardButton(
            topic.title(), 
            callback_data=f"topic:{topic}"
        )])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🎯 *Welcome to the Quiz Bot!*\n\n"
        "📚 *Features:*\n"
        "• Multiple choice questions\n"
        "• Shuffled answer choices\n"
        "• No time limits\n"
        "• Progress tracking\n\n"
        "Select a subject to begin:",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command"""
    help_text = (
        "🤖 *Quiz Bot Help*\n\n"
        "📚 *Available Commands:*\n"
        "• /start - Start the bot and select quiz\n"
        "• /stats - View your quiz statistics\n"
        "• /progress - View your recent progress\n"
        "• /cancel - Cancel current quiz\n"
        "• /help - Show this help message\n\n"
        "🎯 *How to Use:*\n"
        "1. Use /start to begin\n"
        "2. Select a subject and topic\n"
        "3. Answer questions at your own pace\n"
        "4. View your results at the end\n\n"
        "📝 *Quiz Format:*\n"
        "• Questions have 4 multiple choices\n"
        "• Answers are shuffled for each question\n"
        "• No time limits - take your time!\n"
        "• Your progress is automatically saved"
    )
    
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /stats command"""
    user = update.effective_user
    stats = db.get_user_stats(user.id)
    
    if not stats or stats['total_quizzes'] == 0:
        await update.message.reply_text(
            "📊 You haven't completed any quizzes yet.\n"
            "Use /start to begin your first quiz!"
        )
        return
    
    stats_text = (
        f"📊 *Your Quiz Statistics*\n\n"
        f"• Total Quizzes: {stats['total_quizzes']}\n"
        f"• Average Score: {stats['average_score']}%\n\n"
        f"📈 *Recent Quizzes:*\n"
    )
    
    for topic, subtopic, score, total, completed_at in stats['recent_quizzes']:
        percentage = (score / total) * 100 if total > 0 else 0
        date = completed_at.split()[0]  # Get just the date part
        stats_text += f"• {topic}/{subtopic}: {score}/{total} ({percentage:.1f}%) - {date}\n"
    
    await update.message.reply_text(stats_text, parse_mode="Markdown")

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle all callback queries"""
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data
    
    try:
        if callback_data.startswith("topic:"):
            await handle_topic_selection(update, context)
        elif callback_data.startswith("subtopic:"):
            await handle_subtopic_selection(update, context)
        elif callback_data == "main_menu":
            await handle_main_menu(update, context)
        else:
            logger.warning(f"Unknown callback data: {callback_data}")
            await query.edit_message_text("❌ Invalid selection. Please use /start to begin again.")
            
    except Exception as e:
        logger.error(f"Error handling callback {callback_data}: {e}")
        await query.edit_message_text("❌ An error occurred. Please try again.")

async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle return to main menu"""
    query = update.callback_query
    topics = FileManager.list_topics()
    
    keyboard = []
    for topic in topics:
        keyboard.append([InlineKeyboardButton(
            topic.title(), 
            callback_data=f"topic:{topic}"
        )])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "📚 Select a subject:",
        reply_markup=reply_markup
    )

async def handle_topic_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle topic selection"""
    query = update.callback_query
    topic = query.data.split(":")[1]
    
    subtopics = FileManager.list_subtopics(topic)
    if not subtopics:
        await query.edit_message_text(f"❌ No quizzes available for *{topic}*", parse_mode="Markdown")
        return
    
    keyboard = []
    for subtopic in subtopics:
        keyboard.append([InlineKeyboardButton(
            subtopic.title(),
            callback_data=f"subtopic:{topic}:{subtopic}"
        )])
    
    # Add back button
    keyboard.append([InlineKeyboardButton("« Back to Subjects", callback_data="main_menu")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"🧩 *{topic.title()}* - Choose a topic:",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

async def handle_subtopic_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle subtopic selection and start quiz"""
    query = update.callback_query
    _, topic, subtopic = query.data.split(":")
    
    # Load questions
    questions = FileManager.load_questions(topic, subtopic)
    if not questions:
        await query.edit_message_text("❌ No questions found for this topic.")
        return
    
    # Limit questions if configured
    if len(questions) > CONFIG["max_questions_per_quiz"]:
        questions = questions[:CONFIG["max_questions_per_quiz"]]
    
    # Initialize quiz state
    context.user_data.update({
        "quiz_active": True,
        "questions": questions,
        "current_question": 0,
        "correct_answers": 0,
        "topic": topic,
        "subtopic": subtopic,
        "chat_id": query.message.chat_id,
        "start_time": datetime.now().isoformat()
    })
    
    await query.edit_message_text(
        f"🎯 Starting *{topic.title()} - {subtopic.title()}* quiz!\n\n"
        f"• Total questions: {len(questions)}\n"
        f"• Answer choices are shuffled\n"
        f"• No time limits\n"
        f"• Take your time to think!\n\n"
        f"Good luck! 🍀",
        parse_mode="Markdown"
    )
    
    await asyncio.sleep(2)
    await send_next_question(update, context)

async def send_next_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
    
    # Get and shuffle current question
    original_question = questions[current_index]
    shuffled_question = QuizManager.shuffle_choices(original_question)
    user_data["current_shuffled"] = shuffled_question
    
    # Create question text with progress
    progress = f"Question {current_index + 1}/{len(questions)}\n\n"
    question_text = progress + shuffled_question["question"]
    
    try:
        # Send poll
        message = await context.bot.send_poll(
            chat_id=chat_id,
            question=question_text,
            options=shuffled_question["options"],
            type="quiz",
            correct_option_id=shuffled_question["correct_index"],
            is_anonymous=False,
        )
        
        # Store poll information
        user_data["active_poll_id"] = message.poll.id
        user_data["poll_message_id"] = message.message_id
        
        logger.info(f"Sent question {current_index + 1} to user {chat_id}")
        
    except Exception as e:
        logger.error(f"Error sending question {current_index + 1}: {e}")
        # Skip to next question on error
        user_data["current_question"] += 1
        await asyncio.sleep(2)
        await send_next_question(update, context)

async def handle_poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle poll answers"""
    poll_answer = update.poll_answer
    user_data = context.user_data
    
    # Validate this is our active poll
    if user_data.get("active_poll_id") != poll_answer.poll_id:
        return
    
    if not user_data.get("quiz_active"):
        return
    
    # Get current question data
    shuffled_question = user_data.get("current_shuffled")
    if not shuffled_question:
        logger.error("No shuffled question data found")
        return
    
    # Check answer
    user_answer = poll_answer.option_ids[0] if poll_answer.option_ids else None
    is_correct = user_answer == shuffled_question["correct_index"]
    
    if is_correct:
        user_data["correct_answers"] += 1
        feedback = "✅ Correct! Well done!"
    else:
        correct_letter = shuffled_question["shuffled_correct_letter"]
        feedback = f"❌ Incorrect. The correct answer was {correct_letter}"
    
    # Send feedback
    try:
        await context.bot.send_message(
            chat_id=user_data["chat_id"],
            text=feedback,
            reply_to_message_id=user_data.get("poll_message_id")
        )
    except Exception as e:
        logger.error(f"Error sending feedback: {e}")
    
    # Stop the poll
    try:
        await context.bot.stop_poll(
            chat_id=user_data["chat_id"],
            message_id=user_data.get("poll_message_id")
        )
    except Exception as e:
        logger.warning(f"Could not stop poll: {e}")
    
    # Clean up and move to next question
    user_data["current_question"] += 1
    user_data["active_poll_id"] = None
    user_data["poll_message_id"] = None
    
    if "current_shuffled" in user_data:
        del user_data["current_shuffled"]
    
    await asyncio.sleep(CONFIG["time_between_questions"])
    await send_next_question(update, context)

async def finish_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Finish the quiz and show results"""
    user_data = context.user_data
    user = update.effective_user
    
    if not user_data.get("quiz_active"):
        return
    
    correct = user_data["correct_answers"]
    total = len(user_data["questions"])
    percentage = (correct / total) * 100 if total > 0 else 0
    
    # Determine performance message
    if percentage >= 90:
        performance = "🎉 Outstanding! You're a quiz master! 🏆"
    elif percentage >= 75:
        performance = "👍 Great job! You know your stuff! ⭐"
    elif percentage >= 60:
        performance = "😊 Good work! Keep practicing! ✨"
    else:
        performance = "📚 Keep studying! You'll get better! 💪"
    
    # Save progress to database
    db.save_user_progress(
        user_id=user.id,
        topic=user_data["topic"],
        subtopic=user_data["subtopic"],
        score=correct,
        total_questions=total
    )
    
    # Send results
    results_text = (
        f"🎯 *Quiz Completed!*\n\n"
        f"{performance}\n\n"
        f"📊 *Final Score:* {correct}/{total} ({percentage:.1f}%)\n"
        f"📚 *Topic:* {user_data['topic'].title()}\n"
        f"🧩 *Subtopic:* {user_data['subtopic'].title()}\n\n"
        f"Use /start to try another quiz!"
    )
    
    await context.bot.send_message(
        chat_id=user_data["chat_id"],
        text=results_text,
        parse_mode="Markdown"
    )
    
    # Clear quiz state
    user_data.clear()
    logger.info(f"Quiz completed for user {user.id}: {correct}/{total} ({percentage:.1f}%)")

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /cancel command"""
    user_data = context.user_data
    
    if user_data.get("quiz_active"):
        # Stop active poll if exists
        try:
            if user_data.get("active_poll_id"):
                await context.bot.stop_poll(
                    chat_id=user_data["chat_id"],
                    message_id=user_data.get("poll_message_id")
                )
        except Exception as e:
            logger.warning(f"Could not stop poll during cancel: {e}")
        
        user_data.clear()
        await update.message.reply_text("❌ Quiz cancelled. Use /start to begin a new one.")
    else:
        await update.message.reply_text("ℹ️ No active quiz to cancel.")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors in the bot"""
    logger.error(f"Exception while handling an update: {context.error}", exc_info=context.error)
    
    # Try to notify user
    try:
        if update and update.effective_chat:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ An error occurred. Please use /start to begin again."
            )
    except Exception as e:
        logger.error(f"Error sending error message: {e}")

# ==============================
# BOT SETUP AND STARTUP
# ==============================

def main():
    """Start the bot"""
    # Validate configuration
    if not CONFIG["token"]:
        logger.error("No bot token provided. Set TELEGRAM_BOT_TOKEN environment variable.")
        return
    
    # Create necessary directories
    os.makedirs(CONFIG["data_dir"], exist_ok=True)
    
    # Initialize application
    application = Application.builder().token(CONFIG["token"]).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("cancel", cancel_command))
    application.add_handler(CallbackQueryHandler(handle_callback))
    application.add_handler(PollAnswerHandler(handle_poll_answer))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start the bot
    logger.info("🤖 Quiz Bot is starting...")
    logger.info(f"📁 Data directory: {os.path.abspath(CONFIG['data_dir'])}")
    logger.info(f"💾 Database file: {CONFIG['database_file']}")
    
    # List available topics
    topics = FileManager.list_topics()
    if topics:
        logger.info(f"📚 Available topics: {', '.join(topics)}")
    else:
        logger.warning("⚠️ No quiz topics found. Add CSV files to the data directory.")
    
    # Start polling
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        poll_interval=1,
        timeout=30,
        drop_pending_updates=True
    )

if __name__ == "__main__":
    main()