"""
Database management - SIMPLE WORKING VERSION
"""
import sqlite3
import logging
import os
import requests
from typing import Dict

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_file: str):
        self.db_file = db_file
        self.admin_bot_token = os.getenv("ADMIN_BOT_TOKEN")
        self.admin_chat_id = os.getenv("ADMIN_CHAT_ID")
        self.init_database()  # FIXED: Correct spelling
    
    def init_database(self):  # FIXED: Correct spelling
        """Initialize database tables"""
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
    
    def send_to_admin(self, user_id: int, username: str, first_name: str, last_name: str):
        """Send user info to admin bot"""
        if not self.admin_bot_token or not self.admin_chat_id:
            return
        
        message = (
            f"🆕 New User Started Bot:\n"
            f"👤 ID: `{user_id}`\n"
            f"📛 Username: @{username or 'No username'}\n" 
            f"👨‍💼 Name: {first_name or ''} {last_name or ''}"
        )
        
        try:
            requests.post(
                f"https://api.telegram.org/bot{self.admin_bot_token}/sendMessage",
                json={
                    "chat_id": self.admin_chat_id,
                    "text": message,
                    "parse_mode": "Markdown"
                },
                timeout=10
            )
            logger.info(f"✅ Admin notified about user {user_id}")
        except Exception as e:
            logger.warning(f"⚠️ Could not notify admin: {e}")
    
    def update_user(self, user_id: int, username: str, first_name: str, last_name: str):
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
                existing_user = cursor.fetchone()
                
                if not existing_user:
                    cursor.execute('''
                        INSERT INTO users (user_id, username, first_name, last_name)
                        VALUES (?, ?, ?, ?)
                    ''', (user_id, username, first_name, last_name))
                    conn.commit()
                    
                    # Send to admin bot
                    self.send_to_admin(user_id, username, first_name, last_name)
                    
                    logger.info(f"✅ New user added: {user_id}")
                else:
                    cursor.execute('''
                        UPDATE users SET username = ?, first_name = ?, last_name = ?
                        WHERE user_id = ?
                    ''', (username, first_name, last_name, user_id))
                    conn.commit()
                    
        except sqlite3.Error as e:
            logger.error(f"❌ Error updating user {user_id}: {e}")
    
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
                logger.info(f"✅ Saved progress for user {user_id}: {score}/{total_questions}")
        except sqlite3.Error as e:
            logger.error(f"❌ Error saving progress: {e}")
    
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
            logger.error(f"❌ Error getting stats: {e}")
            return {'total_quizzes': 0, 'average_score': 0}