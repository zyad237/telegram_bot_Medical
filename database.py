"""
Database management with Google Sheets logging
"""
import sqlite3
import logging
import os
import gspread
from google.oauth2.service_account import Credentials
from typing import Dict

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_file: str):
        self.db_file = db_file
        self.admin_bot_token = os.getenv("ADMIN_BOT_TOKEN")
        self.admin_chat_id = os.getenv("ADMIN_CHAT_ID")
        self.setup_google_sheets()
        self.init_database()
    
    def setup_google_sheets(self):
        """Setup Google Sheets connection using Railway environment variables"""
        try:
            # Get Google Sheets credentials from Railway
            google_creds_json = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
            spreadsheet_id = os.getenv("GOOGLE_SHEET_ID")
            
            if google_creds_json and spreadsheet_id:
                # Parse JSON credentials from environment variable
                import json
                creds_dict = json.loads(google_creds_json)
                
                # Authenticate with Google Sheets
                scope = ['https://www.googleapis.com/auth/spreadsheets']
                creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
                self.gc = gspread.authorize(creds)
                self.sheet = self.gc.open_by_key(spreadsheet_id).sheet1
                
                # Setup headers if sheet is empty
                if not self.sheet.get_all_records():
                    self.sheet.append_row(["User ID", "Username", "First Name", "Last Name", "Timestamp"])
                
                logger.info("✅ Google Sheets connected successfully")
            else:
                self.sheet = None
                logger.info("ℹ️ Google Sheets not configured")
                
        except Exception as e:
            logger.error(f"❌ Google Sheets setup error: {e}")
            self.sheet = None
    
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
    
    def log_to_google_sheets(self, user_id: int, username: str, first_name: str, last_name: str):
        """Log user to Google Sheets"""
        if not self.sheet:
            return
        
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            self.sheet.append_row([
                user_id,
                f"@{username}" if username else "No username",
                first_name,
                last_name or "",
                timestamp
            ])
            logger.info(f"✅ User {user_id} logged to Google Sheets")
        except Exception as e:
            logger.error(f"❌ Google Sheets logging error: {e}")
    
    def update_user(self, user_id: int, username: str, first_name: str, last_name: str):
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                # Check if user already exists
                cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
                existing_user = cursor.fetchone()
                
                if not existing_user:
                    # New user - insert and log
                    cursor.execute('''
                        INSERT INTO users (user_id, username, first_name, last_name)
                        VALUES (?, ?, ?, ?)
                    ''', (user_id, username, first_name, last_name))
                    conn.commit()
                    
                    # Log to Google Sheets
                    self.log_to_google_sheets(user_id, username, first_name, last_name)
                    
                    logger.info(f"✅ New user added: {user_id}")
                else:
                    # Existing user - update if needed
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