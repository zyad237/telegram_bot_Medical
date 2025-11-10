"""
Database management - CLEAN VERSION (No Google Sheets)
"""
import sqlite3
import logging
from typing import Dict

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_file: str):
        self.db_file = db_file
        self.init_database()
    
    def init_database(self):
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
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS essay_progress (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        essay_id TEXT NOT NULL,
                        question TEXT NOT NULL,
                        user_response TEXT NOT NULL,
                        score REAL DEFAULT 0,
                        feedback TEXT,
                        key_concepts TEXT,
                        essential_terms TEXT,
                        completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')
                conn.commit()
                logger.info("✅ Database initialized successfully")
        except sqlite3.Error as e:
            logger.error(f"❌ Database error: {e}")
    
    def update_user(self, user_id: int, username: str, first_name: str, last_name: str):
        """Update or create user record"""
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
                logger.info(f"✅ Saved progress for user {user_id}: {score}/{total_questions}")
        except sqlite3.Error as e:
            logger.error(f"❌ Error saving progress: {e}")
    
    def save_essay_progress(self, user_id: int, essay_id: str, question: str, user_response: str, 
                           score: float, feedback: str, key_concepts: str, essential_terms: str):
        """Save user essay progress"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO essay_progress 
                    (user_id, essay_id, question, user_response, score, feedback, key_concepts, essential_terms)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, essay_id, question, user_response, score, feedback, key_concepts, essential_terms))
                conn.commit()
                logger.info(f"✅ Saved essay progress for user {user_id}: {score}/10")
        except sqlite3.Error as e:
            logger.error(f"❌ Error saving essay progress: {e}")
    
    def get_user_stats(self, user_id: int) -> Dict:
        """Get user statistics"""
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
                
                cursor.execute('SELECT COUNT(*) FROM essay_progress WHERE user_id = ?', (user_id,))
                total_essays = cursor.fetchone()[0] or 0
                
                cursor.execute('SELECT AVG(score) FROM essay_progress WHERE user_id = ?', (user_id,))
                avg_essay_score = cursor.fetchone()[0] or 0
                
                return {
                    'total_quizzes': total_quizzes,
                    'average_score': round(avg_score, 1),
                    'total_essays': total_essays,
                    'average_essay_score': round(avg_essay_score, 1)
                }
        except sqlite3.Error as e:
            logger.error(f"❌ Error getting stats: {e}")
            return {
                'total_quizzes': 0, 
                'average_score': 0,
                'total_essays': 0,
                'average_essay_score': 0
            }