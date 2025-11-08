"""
Database management with Google Sheets analytics
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
        self.setup_google_sheets()
        self.init_database()
    
    def setup_google_sheets(self):
        """Setup Google Sheets connection"""
        try:
            # Method 1: Base64 encoded credentials
            encoded_creds = os.getenv("GOOGLE_CREDENTIALS_BASE64")
            spreadsheet_id = os.getenv("GOOGLE_SHEET_ID")
            
            if encoded_creds and spreadsheet_id:
                # Decode base64 credentials
                creds_json = base64.b64decode(encoded_creds).decode('utf-8')
                creds_dict = json.loads(creds_json)
                
                scope = [
                    'https://www.googleapis.com/auth/spreadsheets',
                    'https://www.googleapis.com/auth/drive'
                ]
                creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
                self.gc = gspread.authorize(creds)
                
                # Try to open existing sheet or create new
                try:
                    self.spreadsheet = self.gc.open_by_key(spreadsheet_id)
                except:
                    # Create new spreadsheet if doesn't exist
                    self.spreadsheet = self.gc.create("Medical Quiz Analytics")
                    self.spreadsheet.share(creds_dict['client_email'], perm_type='user', role='writer')
                
                # Setup worksheets
                self.setup_worksheets()
                logger.info("✅ Google Sheets analytics connected")
                
            else:
                self.spreadsheet = None
                logger.warning("ℹ️ Google Sheets not configured")
                
        except Exception as e:
            logger.error(f"❌ Google Sheets setup error: {e}")
            self.spreadsheet = None
    
    def setup_worksheets(self):
        """Create and setup different analytics sheets"""
        worksheets = {
            'users': ['User ID', 'Username', 'First Name', 'Last Name', 'Join Date', 'Total Quizzes', 'Avg Score'],
            'quiz_activity': ['Date', 'User ID', 'Topic', 'Subtopic', 'Score', 'Total Questions', 'Percentage'],
            'daily_stats': ['Date', 'New Users', 'Total Quizzes', 'Avg Score', 'Active Users'],
            'popular_quizzes': ['Topic', 'Subtopic', 'Total Attempts', 'Avg Score']
        }
        
        for sheet_name, headers in worksheets.items():
            try:
                worksheet = self.spreadsheet.worksheet(sheet_name)
            except:
                worksheet = self.spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=len(headers))
                worksheet.append_row(headers)
    
    def log_new_user(self, user_id: int, username: str, first_name: str, last_name: str):
        """Log new user to analytics"""
        if not self.spreadsheet:
            return
        
        try:
            users_sheet = self.spreadsheet.worksheet('users')
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Check if user already exists
            try:
                cell = users_sheet.find(str(user_id))
                # User exists, update if needed
                users_sheet.update_cell(cell.row, 2, f"@{username}" if username else "No username")
                users_sheet.update_cell(cell.row, 3, first_name or "")
                users_sheet.update_cell(cell.row, 4, last_name or "")
            except:
                # New user
                users_sheet.append_row([
                    str(user_id),
                    f"@{username}" if username else "No username",
                    first_name or "",
                    last_name or "",
                    timestamp,
                    "0",  # Total Quizzes
                    "0%"  # Avg Score
                ])
            
            # Update daily stats
            self.update_daily_stats('new_users')
            
            logger.info(f"✅ User {user_id} logged to analytics")
        except Exception as e:
            logger.error(f"❌ User analytics error: {e}")
    
    def log_quiz_activity(self, user_id: int, topic: str, subtopic: str, score: int, total_questions: int):
        """Log quiz completion to analytics"""
        if not self.spreadsheet:
            return
        
        try:
            # Quiz activity sheet
            activity_sheet = self.spreadsheet.worksheet('quiz_activity')
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
            
            # Update user stats
            self.update_user_stats(user_id)
            
            # Update daily stats
            self.update_daily_stats('quizzes')
            
            # Update popular quizzes
            self.update_popular_quizzes(topic, subtopic, percentage)
            
            logger.info(f"✅ Quiz activity logged for user {user_id}")
        except Exception as e:
            logger.error(f"❌ Quiz analytics error: {e}")
    
    def update_user_stats(self, user_id: int):
        """Update user's total quizzes and average score"""
        try:
            users_sheet = self.spreadsheet.worksheet('users')
            activity_sheet = self.spreadsheet.worksheet('quiz_activity')
            
            # Find user row
            cell = users_sheet.find(str(user_id))
            if not cell:
                return
            
            # Get user's quiz history
            user_activities = [row for row in activity_sheet.get_all_records() 
                             if str(row['User ID']) == str(user_id)]
            
            total_quizzes = len(user_activities)
            avg_score = 0
            
            if total_quizzes > 0:
                total_percentage = sum(float(act['Percentage'].rstrip('%')) for act in user_activities)
                avg_score = total_percentage / total_quizzes
            
            # Update user row
            users_sheet.update_cell(cell.row, 6, str(total_quizzes))  # Total Quizzes
            users_sheet.update_cell(cell.row, 7, f"{avg_score:.1f}%")  # Avg Score
            
        except Exception as e:
            logger.error(f"❌ User stats update error: {e}")
    
    def update_daily_stats(self, metric: str):
        """Update daily statistics"""
        try:
            daily_sheet = self.spreadsheet.worksheet('daily_stats')
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Find today's row or create new
            try:
                cell = daily_sheet.find(today)
                row = cell.row
            except:
                daily_sheet.append_row([today, "0", "0", "0%", "0"])
                row = len(daily_sheet.get_all_records())
            
            # Update metric
            if metric == 'new_users':
                current = int(daily_sheet.cell(row, 2).value or 0)
                daily_sheet.update_cell(row, 2, str(current + 1))
            elif metric == 'quizzes':
                current = int(daily_sheet.cell(row, 3).value or 0)
                daily_sheet.update_cell(row, 3, str(current + 1))
                
        except Exception as e:
            logger.error(f"❌ Daily stats error: {e}")
    
    def update_popular_quizzes(self, topic: str, subtopic: str, percentage: float):
        """Update popular quizzes statistics"""
        try:
            popular_sheet = self.spreadsheet.worksheet('popular_quizzes')
            quiz_identifier = f"{topic} - {subtopic}"
            
            # Find quiz or create new entry
            try:
                cell = popular_sheet.find(quiz_identifier)
                row = cell.row
                attempts = int(popular_sheet.cell(row, 3).value or 0) + 1
                current_avg = float(popular_sheet.cell(row, 4).value or 0)
                new_avg = ((current_avg * (attempts - 1)) + percentage) / attempts
                
                popular_sheet.update_cell(row, 3, str(attempts))
                popular_sheet.update_cell(row, 4, f"{new_avg:.1f}%")
            except:
                popular_sheet.append_row([
                    quiz_identifier,
                    subtopic,
                    "1",
                    f"{percentage}%"
                ])
                
        except Exception as e:
            logger.error(f"❌ Popular quizzes error: {e}")
    
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
                    
                    # Analytics logging
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
                
                # Analytics logging
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