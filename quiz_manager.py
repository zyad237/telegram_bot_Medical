"""
Quiz logic and management for 6-level navigation
"""
import random
import asyncio
import logging
from typing import Dict, List

from telegram import Update
from telegram.ext import CallbackContext

from config import CONFIG
from file_manager import FileManager
from database import DatabaseManager

logger = logging.getLogger(__name__)

class QuizManager:
    def __init__(self, database: DatabaseManager):
        self.db = database
    
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

    def _get_subtopic_filename(self, year: str, term: str, block: str, subject: str, category: str, subtopic_number: str) -> str:
        """Convert subtopic number back to actual filename"""
        subtopics = FileManager.list_subtopics(year, term, block, subject, category)
        print(f"🔍 Looking for subtopic {subtopic_number} in: {subtopics}")
        
        for filename in subtopics:
            # Check if filename starts with the number (with underscore)
            if filename.startswith(f"{subtopic_number}_"):
                print(f"✅ Found matching file: {filename}")
                return filename
            
            # Also check if the number part matches (without leading zeros)
            if filename.split('_')[0].lstrip('0') == subtopic_number.lstrip('0'):
                print(f"✅ Found matching file (number only): {filename}")
                return filename
        
        print(f"❌ No file found for subtopic number: {subtopic_number}")
        return subtopic_number  # Fallback

    async def start_quiz(self, update: Update, context: CallbackContext, year: str, term: str, block: str, subject: str, category: str, subtopic_number: str):
        """Start a new quiz with 6-level navigation"""
        query = update.callback_query
        
        # Convert number back to actual filename
        actual_filename = self._get_subtopic_filename(year, term, block, subject, category, subtopic_number)
        print(f"📁 Loading questions for file: {actual_filename}")
        
        questions = FileManager.load_questions(year, term, block, subject, category, actual_filename)
        
        if not questions:
            year_display = FileManager.get_year_display_name(year)
            term_display = FileManager.get_term_display_name(year, term)
            block_display = FileManager.get_block_display_name(year, term, block)
            subject_display = FileManager.get_subject_display_name(year, term, block, subject)
            category_display = FileManager.get_category_display_name(year, term, block, subject, category)
            subtopic_display = FileManager.get_subtopic_display_name(year, term, block, subject, category, actual_filename)
            
            print(f"❌ No questions found for: {year}/{term}/{block}/{subject}/{category}/{actual_filename}")
            print(f"   File path: data/{year}/{term}/{block}/{subject}/{category}/{actual_filename}")
            
            await query.edit_message_text(
                f"❌ No valid questions found for:\n"
                f"📅 {year_display} - {term_display} - {block_display}\n"
                f"📚 {subject_display} - {category_display}\n"
                f"🧩 {subtopic_display}\n\n"
                f"Please check if the CSV file exists and has the correct format."
            )
            return False
        
        if len(questions) > CONFIG["max_questions_per_quiz"]:
            questions = questions[:CONFIG["max_questions_per_quiz"]]
        
        context.user_data.update({
            "quiz_active": True,
            "questions": questions,
            "current_question": 0,
            "correct_answers": 0,
            "year": year,
            "term": term,
            "block": block,
            "subject": subject,
            "category": category,
            "subtopic": actual_filename,  # Store actual filename
            "chat_id": query.message.chat_id,
        })
        
        year_display = FileManager.get_year_display_name(year)
        term_display = FileManager.get_term_display_name(year, term)
        block_display = FileManager.get_block_display_name(year, term, block)
        subject_display = FileManager.get_subject_display_name(year, term, block, subject)
        category_display = FileManager.get_category_display_name(year, term, block, subject, category)
        subtopic_display = FileManager.get_subtopic_display_name(year, term, block, subject, category, actual_filename)
        
        await query.edit_message_text(
            f"🎯 Starting Quiz!\n\n"
            f"📅 {year_display} - {term_display} - {block_display}\n"
            f"📚 {subject_display} - {category_display}\n"
            f"🧩 {subtopic_display}\n\n"
            f"• Total questions: {len(questions)}\n"
            f"• Answer choices are shuffled\n"
            f"• No time limits\n\n"
            f"Good luck! 🍀"
        )
        
        await asyncio.sleep(2)
        await self.send_next_question(update, context)
        return True

    async def send_next_question(self, update: Update, context: CallbackContext):
        """Send the next question in the quiz"""
        user_data = context.user_data
        
        print(f"🔍 SEND_NEXT_QUESTION called")
        print(f"   Quiz active: {user_data.get('quiz_active')}")
        print(f"   Current question: {user_data.get('current_question')}")
        print(f"   Total questions: {len(user_data.get('questions', []))}")
        
        if not user_data.get("quiz_active"):
            print(f"❌ Quiz not active - returning")
            return
        
        current_index = user_data["current_question"]
        questions = user_data["questions"]
        chat_id = user_data["chat_id"]
        
        if current_index >= len(questions):
            print(f"🎯 Quiz finished - calling finish_quiz")
            await self.finish_quiz(update, context)
            return
        
        print(f"📝 Sending question {current_index + 1}/{len(questions)}")
        
        original_question = questions[current_index]
        shuffled_question = self.shuffle_choices(original_question)
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
            
            print(f"✅ Question {current_index + 1} sent successfully")
            print(f"   Poll ID: {message.poll.id}")
            print(f"   Message ID: {message.message_id}")
            
        except Exception as e:
            print(f"❌ Error sending question {current_index + 1}: {e}")
            user_data["current_question"] += 1
            await asyncio.sleep(2)
            await self.send_next_question(update, context)

    async def handle_poll_answer(self, update: Update, context: CallbackContext):
        """Handle poll answers"""
        poll_answer = update.poll_answer
        user_data = context.user_data
        
        print(f"🎯 POLL ANSWER RECEIVED:")
        print(f"   Poll ID: {poll_answer.poll_id}")
        print(f"   User ID: {poll_answer.user.id}")
        print(f"   Option IDs: {poll_answer.option_ids}")
        print(f"   Active Poll ID in user_data: {user_data.get('active_poll_id')}")
        print(f"   Quiz Active: {user_data.get('quiz_active')}")
        
        # Check if this is our poll
        if user_data.get("active_poll_id") != poll_answer.poll_id:
            print(f"❌ Poll ID mismatch - ignoring")
            return
        
        if not user_data.get("quiz_active"):
            print(f"❌ Quiz not active - ignoring")
            return
        
        shuffled_question = user_data.get("current_shuffled")
        if not shuffled_question:
            print(f"❌ No current shuffled question - ignoring")
            return
        
        user_answer = poll_answer.option_ids[0] if poll_answer.option_ids else None
        is_correct = user_answer == shuffled_question["correct_index"]
        
        print(f"   User answer: {user_answer}")
        print(f"   Correct index: {shuffled_question['correct_index']}")
        print(f"   Is correct: {is_correct}")
        
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
            print(f"✅ Feedback sent: {feedback}")
        except Exception as e:
            print(f"❌ Error sending feedback: {e}")
        
        # Stop the poll
        try:
            await context.bot.stop_poll(
                chat_id=user_data["chat_id"],
                message_id=user_data.get("poll_message_id")
            )
            print(f"✅ Poll stopped")
        except Exception as e:
            print(f"⚠️ Could not stop poll: {e}")
        
        # Move to next question
        user_data["current_question"] += 1
        user_data["active_poll_id"] = None
        user_data["poll_message_id"] = None
        
        if "current_shuffled" in user_data:
            del user_data["current_shuffled"]
        
        print(f"📊 Progress: {user_data['current_question']}/{len(user_data['questions'])}")
        print(f"📈 Correct answers: {user_data['correct_answers']}")
        
        await asyncio.sleep(CONFIG["time_between_questions"])
        await self.send_next_question(update, context)

    async def finish_quiz(self, update: Update, context: CallbackContext):
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
        
        # Save progress with all 6 levels
        self.db.save_user_progress(
            user_id=user.id,
            topic=f"{user_data['year']}_{user_data['term']}_{user_data['block']}_{user_data['subject']}",
            subtopic=f"{user_data['category']}_{user_data['subtopic']}",
            score=correct,
            total_questions=total
        )
        
        # Get display names for results
        year_display = FileManager.get_year_display_name(user_data["year"])
        term_display = FileManager.get_term_display_name(user_data["year"], user_data["term"])
        block_display = FileManager.get_block_display_name(user_data["year"], user_data["term"], user_data["block"])
        subject_display = FileManager.get_subject_display_name(user_data["year"], user_data["term"], user_data["block"], user_data["subject"])
        category_display = FileManager.get_category_display_name(user_data["year"], user_data["term"], user_data["block"], user_data["subject"], user_data["category"])
        subtopic_display = FileManager.get_subtopic_display_name(user_data["year"], user_data["term"], user_data["block"], user_data["subject"], user_data["category"], user_data["subtopic"])
        
        results_text = (
            f"🎯 Quiz Completed!\n\n"
            f"{performance}\n\n"
            f"📊 Final Score: {correct}/{total} ({percentage:.1f}%)\n\n"
            f"📅 {year_display} - {term_display} - {block_display}\n"
            f"📚 {subject_display} - {category_display}\n"
            f"🧩 {subtopic_display}\n\n"
            f"Use /start to try another quiz!"
        )
        
        await context.bot.send_message(
            chat_id=user_data["chat_id"],
            text=results_text
        )
        
        user_data.clear()
        logger.info(f"✅ Quiz completed for user {user.id}: {correct}/{total} ({percentage:.1f}%)")