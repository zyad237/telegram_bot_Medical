"""
Database management with Google Sheets analytics - FIXED VERSION
"""
import sqlite3
import logging
import os
import requests
import gspread
import json
import base64
from google.oauth2.service_account import Credentials
from typing import Dict
from datetime import datetime

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_file: str):
        self.db_file = db_file
        self.admin_bot_token = os.getenv("ADMIN_BOT_TOKEN")
        self.admin_chat_id = os.getenv("ADMIN_CHAT_ID")
        self.spreadsheet = None  # Initialize to avoid attribute errors
        self.setup_google_sheets()
        self.init_database()  # FIXED: Correct method name
    
    def setup_google_sheets(self):
        """Setup Google Sheets connection - SIMPLIFIED"""
        try:
            # Get credentials from environment
            encoded_creds = os.getenv("GOOGLE_CREDENTIALS_BASE64")
            spreadsheet_id = os.getenv("GOOGLE_SHEET_ID")
            
            if not encoded_creds or not spreadsheet_id:
                logger.warning("ℹ️ Google Sheets not configured - skipping analytics")
                return
            
            # Decode base64 credentials
            creds_json = base64.b64decode(encoded_creds).decode('utf-8')
            creds_dict = json.loads(creds_json)
            
            # Print service account email for debugging
            service_email = creds_dict.get('client_email', 'Unknown')
            logger.info(f"🔧 Service Account: {service_email}")
            
            # Authenticate
            scope = ['https://www.googleapis.com/auth/spreadsheets']
            creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
            self.gc = gspread.authorize(creds)
            
            # Try to access the sheet
            self.spreadsheet = self.gc.open_by_key(spreadsheet_id)
            
            logger.info("✅ Google Sheets analytics connected")
            
        except Exception as e:
            logger.error(f"❌ Google Sheets setup error: {e}")
            self.spreadsheet = None
    
    def init_database(self):  # FIXED: Correct method name
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
    
    def log_new_user(self, user_id: int, username: str, first_name: str, last_name: str):
        """Log new user to analytics - SAFE VERSION"""
        if not self.spreadsheet:
            return  # Skip if sheets not configured
        
        try:
            # Get or create users worksheet
            try:
                users_sheet = self.spreadsheet.worksheet('users')
            except:
                users_sheet = self.spreadsheet.add_worksheet(title='users', rows=1000, cols=7)
                users_sheet.append_row(['User ID', 'Username', 'First Name', 'Last Name', 'Join Date', 'Total Quizzes', 'Avg Score'])
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Add new user
            users_sheet.append_row([
                str(user_id),
                f"@{username}" if username else "No username",
                first_name or "",
                last_name or "",
                timestamp,
                "0",
                "0%"
            ])
            
            logger.info(f"✅ User {user_id} logged to analytics")
        except Exception as e:
            logger.error(f"❌ User analytics error: {e}")
    
    def log_quiz_activity(self, user_id: int, topic: str, subtopic: str, score: int, total_questions: int):
        """Log quiz completion - SAFE VERSION"""
        if not self.spreadsheet:
            return
        
        try:
            # Get or create activity worksheet
            try:
                activity_sheet = self.spreadsheet.worksheet('quiz_activity')
            except:
                activity_sheet = self.spreadsheet.add_worksheet(title='quiz_activity', rows=1000, cols=7)
                activity_sheet.append_row(['Date', 'User ID', 'Topic', 'Subtopic', 'Score', 'Total Questions', 'Percentage'])
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            percentage = round((score / total_questions) * 100, 1) if total_questions > 0 else 0
            
            activity_sheet.append_row([
                timestamp,
                str(user_id),
                topic,
                subtopic,
                str(score),
                str(total_questions),
                f"{percentage}%"
            ])
            
            logger.info(f"✅ Quiz activity logged for user {user_id}")
        except Exception as e:
            logger.error(f"❌ Quiz analytics error: {e}")
    
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
                    
                    # Analytics logging (will skip if sheets not working)
                    self.log_new_user(user_id, username, first_name, last_name)
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
                
                # Analytics logging (will skip if sheets not working)
                self.log_quiz_activity(user_id, topic, subtopic, score, total_questions)
                
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