"""
Simple essay questions manager - short answers, lists, brief elaborations
"""
import logging
import json
from typing import Dict, List
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import asyncio

from ai_manager import AIManager

logger = logging.getLogger(__name__)

class SimpleEssayManager:
    def __init__(self):
        self.ai_manager = AIManager()
        self.essay_types = {
            "list": "📝 List Questions",
            "explain": "💡 Brief Explanation", 
            "compare": "⚖️ Compare & Contrast",
            "define": "📚 Define & Describe"
        }
    
    async def start_essay_session(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                                year: str, term: str, block: str, subject: str, essay_type: str):
        """Start simple essay session"""
        query = update.callback_query
        
        # Load essay questions for this type
        essay_questions = self.load_essay_questions(year, term, block, subject, essay_type)
        
        if not essay_questions:
            await query.edit_message_text(
                f"❌ No {self.essay_types[essay_type]} questions available yet.\n\n"
                f"Check back later or try other question types."
            )
            return False
        
        context.user_data.update({
            "simple_essay_active": True,
            "essay_type": essay_type,
            "essay_questions": essay_questions,
            "current_essay_index": 0,
            "essay_answers": [],
            "year": year,
            "term": term,
            "block": block,
            "subject": subject,
            "chat_id": query.message.chat_id,
            "waiting_for_essay_answer": False
        })
        
        type_display = self.essay_types[essay_type]
        
        await query.edit_message_text(
            f"✍️ {type_display}\n"
            f"📚 Subject: {subject.title()}\n\n"
            f"• You'll answer {len(essay_questions)} questions\n"
            f"• Short answers expected (1-3 sentences)\n"
            f"• AI will evaluate and provide feedback\n"
            f"• Focus on key points and clarity\n\n"
            f"Ready to begin?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Start Questions", callback_data="start_simple_essay")],
                [InlineKeyboardButton("❌ Cancel", callback_data="cancel_simple_essay")]
            ])
        )
        return True
    
    def load_essay_questions(self, year: str, term: str, block: str, subject: str, essay_type: str) -> List[Dict]:
        """Load simple essay questions from JSON"""
        try:
            essay_path = f"data/{year}/{term}/{block}/{subject}/simple_essays/{essay_type}_questions.json"
            
            with open(essay_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("questions", [])
                
        except FileNotFoundError:
            logger.info(f"No {essay_type} questions found at {essay_path}")
            return []
        except Exception as e:
            logger.error(f"Error loading {essay_type} questions: {e}")
            return []
    
    async def send_next_essay_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send the next simple essay question"""
        user_data = context.user_data
        
        if not user_data.get("simple_essay_active"):
            return
        
        current_index = user_data["current_essay_index"]
        questions = user_data["essay_questions"]
        
        if current_index >= len(questions):
            await self.finish_essay_session(update, context)
            return
        
        question_data = questions[current_index]
        question_text = question_data["question"]
        
        # Add question type specific instructions
        instructions = self._get_instructions(user_data["essay_type"])
        
        full_question = f"📝 Question {current_index + 1}/{len(questions)}\n\n{question_text}\n\n{instructions}"
        
        # Add hint if available
        if "hint" in question_data:
            full_question += f"\n\n💡 Hint: {question_data['hint']}"
        
        # Add AI help button
        keyboard = [
            [InlineKeyboardButton("🤖 Get AI Hint", callback_data=f"ai_hint:{current_index}")]
        ]
        
        await context.bot.send_message(
            chat_id=user_data["chat_id"],
            text=full_question,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
        user_data["waiting_for_essay_answer"] = True
        user_data["current_question_data"] = question_data
    
    def _get_instructions(self, essay_type: str) -> str:
        """Get instructions based on essay type"""
        instructions = {
            "list": "🔹 List the main points (2-4 items)\n🔹 Be concise and specific",
            "explain": "🔹 Briefly explain in 1-3 sentences\n🔹 Focus on key concepts", 
            "compare": "🔹 Compare similarities and differences\n🔹 2-3 points for each",
            "define": "🔹 Define the term clearly\n🔹 Describe key characteristics"
        }
        return instructions.get(essay_type, "Provide a clear, concise answer.")
    
    async def handle_essay_answer(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle short essay answers"""
        user_data = context.user_data
        
        if not user_data.get("waiting_for_essay_answer"):
            return
        
        user_answer = update.message.text
        question_data = user_data["current_question_data"]
        subject = user_data["subject"]
        
        # Show evaluating message
        evaluating_msg = await update.message.reply_text("🔍 AI is evaluating your answer...")
        
        try:
            # Evaluate with AI
            evaluation = await self.ai_manager.evaluate_short_essay(
                question_data["question"],
                user_answer,
                subject,
                question_data.get("expected_points", [])
            )
            
            # Store result
            user_data["essay_answers"].append({
                "question": question_data["question"],
                "user_answer": user_answer,
                "evaluation": evaluation,
                "score": evaluation.get("score", 0)
            })
            
            # Send evaluation to user
            await self.send_evaluation_to_user(
                context,
                user_data["chat_id"],
                question_data,
                evaluation,
                evaluating_msg.message_id
            )
            
            # Move to next question
            user_data["current_essay_index"] += 1
            user_data["waiting_for_essay_answer"] = False
            
            if "current_question_data" in user_data:
                del user_data["current_question_data"]
            
            # Brief pause before next question
            await asyncio.sleep(2)
            await self.send_next_essay_question(update, context)
            
        except Exception as e:
            logger.error(f"Error in essay evaluation: {e}")
            await evaluating_msg.edit_text(
                "❌ Error evaluating your answer. Please continue to next question."
            )
    
    async def send_evaluation_to_user(self, context: ContextTypes.DEFAULT_TYPE, chat_id: int,
                                    question_data: Dict, evaluation: Dict, original_message_id: int):
        """Send AI evaluation to user"""
        score = evaluation.get("score", 0)
        strengths = evaluation.get("strengths", [])
        improvements = evaluation.get("improvements", [])
        explanation = evaluation.get("explanation", "")
        suggestion = evaluation.get("suggestion", "")
        
        feedback_text = f"📊 **Evaluation: {score}/5**\n\n"
        
        if strengths:
            feedback_text += "✅ **Strengths:**\n" + "\n".join(f"• {s}" for s in strengths) + "\n\n"
        
        if improvements:
            feedback_text += "📝 **Improve:**\n" + "\n".join(f"• {i}" for i in improvements) + "\n\n"
        
        if explanation:
            feedback_text += f"💡 **Explanation:** {explanation}\n\n"
        
        if suggestion:
            feedback_text += f"🎯 **Suggestion:** {suggestion}"
        
        # Add expected points if available
        if "expected_points" in question_data:
            feedback_text += f"\n\n🔑 **Expected Points:**\n"
            feedback_text += "\n".join(f"• {point}" for point in question_data["expected_points"])
        
        await context.bot.send_message(
            chat_id=chat_id,
            text=feedback_text,
            reply_to_message_id=original_message_id,
            parse_mode="Markdown"
        )
    
    async def handle_ai_hint(self, update: Update, context: ContextTypes.DEFAULT_TYPE, question_index: int):
        """Handle AI hint requests"""
        query = update.callback_query
        user_data = context.user_data
        
        if not user_data.get("simple_essay_active"):
            return
        
        questions = user_data["essay_questions"]
        if question_index < len(questions):
            question_data = questions[question_index]
            subject = user_data["subject"]
            
            await query.answer("Getting AI hint...")
            
            hint = await self.ai_manager.give_hint(question_data, subject)
            
            await context.bot.send_message(
                chat_id=user_data["chat_id"],
                text=f"💡 **AI Hint:**\n\n{hint}",
                parse_mode="Markdown",
                reply_to_message_id=query.message.message_id
            )
    
    async def finish_essay_session(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Finish essay session"""
        user_data = context.user_data
        
        if not user_data.get("simple_essay_active"):
            return
        
        answers = user_data.get("essay_answers", [])
        total_score = sum(answer.get("score", 0) for answer in answers)
        average_score = total_score / len(answers) if answers else 0
        
        type_display = self.essay_types[user_data["essay_type"]]
        subject = user_data["subject"].title()
        
        results_text = (
            f"🎯 Session Complete!\n\n"
            f"📝 Type: {type_display}\n"
            f"📚 Subject: {subject}\n"
            f"📊 Average: {average_score:.1f}/5\n"
            f"✅ Completed: {len(answers)} questions\n\n"
        )
        
        if average_score >= 4:
            results_text += "🏆 Excellent! Strong understanding demonstrated!"
        elif average_score >= 3:
            results_text += "👍 Good work! Solid grasp with minor areas to review."
        else:
            results_text += "📚 Keep practicing! Review the key concepts."
        
        results_text += "\n\nUse /start to practice more!"
        
        await context.bot.send_message(
            chat_id=user_data["chat_id"],
            text=results_text
        )
        
        user_data.clear()
    
    async def handle_simple_essay_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle simple essay callbacks"""
        query = update.callback_query
        callback_data = query.data
        
        if callback_data == "start_simple_essay":
            await query.edit_message_text("Starting questions...")
            await self.send_next_essay_question(update, context)
        elif callback_data == "cancel_simple_essay":
            context.user_data.clear()
            await query.edit_message_text("❌ Session cancelled.")
        elif callback_data.startswith("ai_hint:"):
            question_index = int(callback_data.split(":")[1])
            await self.handle_ai_hint(update, context, question_index)