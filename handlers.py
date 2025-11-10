"""
<<<<<<< Updated upstream
<<<<<<< Updated upstream
Bot command and callback handlers for 6-level navigation with AI integration
"""
import logging
import asyncio
=======
Bot command and callback handlers for 6-level navigation with AI essay support
"""
import logging
import requests
>>>>>>> Stashed changes
=======
Bot command and callback handlers for 6-level navigation with AI essay support
"""
import logging
import requests
>>>>>>> Stashed changes
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, CommandHandler, PollAnswerHandler, MessageHandler, filters
from telegram.error import BadRequest

from file_manager import FileManager
from callback_manager import CallbackManager
from quiz_manager import QuizManager
from database import DatabaseManager
<<<<<<< Updated upstream
<<<<<<< Updated upstream
from ai_manager import AIManager
from simple_essay_manager import SimpleEssayManager
=======
from config import CONFIG, ESSAY_QUESTIONS, get_essay_questions_by_subject
>>>>>>> Stashed changes
=======
from config import CONFIG, ESSAY_QUESTIONS, get_essay_questions_by_subject
>>>>>>> Stashed changes

logger = logging.getLogger(__name__)

class BotHandlers:
    def __init__(self, database: DatabaseManager, quiz_manager: QuizManager):
        self.db = database
        self.quiz_manager = quiz_manager
        self.ai_manager = AIManager()
        self.simple_essay_manager = SimpleEssayManager()
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command - show years"""
        user = update.effective_user
        self.db.update_user(user.id, user.username, user.first_name, user.last_name)
        
        context.user_data.clear()
        years = FileManager.list_years()
        
        if not years:
            await update.message.reply_text("📝 No academic years available.")
            return
        
        keyboard = []
        for year in years:
            callback_data = CallbackManager.create_year_callback(year)
            display_name = FileManager.get_year_display_name(year)
            keyboard.append([InlineKeyboardButton(display_name, callback_data=callback_data)])
        
<<<<<<< Updated upstream
<<<<<<< Updated upstream
        # Add AI help button
        keyboard.append([InlineKeyboardButton("🤖 AI Medical Tutor", callback_data="ai_tutor_menu")])
=======
        # Add essay button to main menu
        keyboard.append([InlineKeyboardButton("📝 Essay Questions", callback_data="essay_main")])
>>>>>>> Stashed changes
=======
        # Add essay button to main menu
        keyboard.append([InlineKeyboardButton("📝 Essay Questions", callback_data="essay_main")])
>>>>>>> Stashed changes
        
        await update.message.reply_text(
            "🎓 Medical Quiz Bot\n\nSelect your academic year or try essay questions:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = (
            "🤖 Medical Quiz Bot Help\n\n"
            "📚 Available Commands:\n"
            "• /start - Start the bot and select quiz\n"
            "• /stats - View your quiz statistics\n"
<<<<<<< Updated upstream
<<<<<<< Updated upstream
            "• /cancel - Cancel current session\n"
            "• /explain - Explain current quiz question\n"
            "• /ai <question> - Ask AI medical tutor\n"
            "• /search <query> - Search college materials\n"
            "• /materials - Show available college PDFs\n"
            "• /help - Show this help message\n\n"
            "🎯 How to Use:\n"
            "1. Use /start to begin\n"
            "2. Navigate: Year → Term → Block → Subject → Category\n"
            "3. Choose between multiple-choice quizzes or essay questions\n"
            "4. Use AI features for explanations and help\n\n"
            "🤖 AI Features:\n"
            "• During quizzes: /explain for question explanations\n"
            "• Any time: /ai <question> for medical tutoring\n"
            "• Search: /search <topic> in college materials\n"
            "• Essay evaluation: AI-powered feedback\n\n"
=======
=======
>>>>>>> Stashed changes
            "• /essay - Practice essay questions with AI grading\n"
            "• /cancel - Cancel current quiz or essay\n"
            "• /help - Show this help message\n\n"
            "🎯 How to Use:\n"
            "1. Use /start to begin\n"
            "2. Navigate: Year → Term → Block → Subject → Category → Quiz\n"
            "3. Answer questions at your own pace\n"
            "4. Get AI explanations for wrong answers\n"
            "5. Try essay questions within each subject\n\n"
            "📝 Essay Features:\n"
            "• Subject-specific essay questions\n"
            "• AI-powered grading with medical context\n"
            "• Spelling-tolerant for medical terminology\n"
            "• Key concept evaluation\n"
            "• Constructive feedback\n\n"
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
            "📖 Navigation:\n"
            "• Years: Academic years\n"
            "• Terms: Semester terms\n"
            "• Blocks: Curriculum blocks\n"
<<<<<<< Updated upstream
<<<<<<< Updated upstream
            "• Subjects: Anatomy, Histology, etc.\n"
            "• Categories: Quizzes, Essays, Simple Essays"
=======
=======
>>>>>>> Stashed changes
            "• Subjects: Anatomy, Histology, Physiology, Biochemistry\n"
            "• Categories: General, Midterm, Final, Essays\n"
            "• Quizzes: Individual topic quizzes"
>>>>>>> Stashed changes
        )
        
        await update.message.reply_text(help_text)
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command"""
        user = update.effective_user
        stats = self.db.get_user_stats(user.id)
        
        if stats['total_quizzes'] == 0 and stats['total_essays'] == 0:
            await update.message.reply_text("📊 You haven't completed any quizzes or essays yet!\nUse /start to begin.")
            return
        
        stats_text = (
            f"📊 Your Quiz Statistics\n\n"
            f"• Total Quizzes Completed: {stats['total_quizzes']}\n"
            f"• Average Quiz Score: {stats['average_score']}%\n"
            f"• Total Essays Completed: {stats['total_essays']}\n"
            f"• Average Essay Score: {stats['average_essay_score']}/10\n\n"
            f"Keep up the great work! 🎯"
        )
        
        await update.message.reply_text(stats_text)
    
    async def essay_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /essay command for essay questions"""
        await self.show_essay_subjects(update, context)
    
    async def show_essay_subjects(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show available subjects for essay questions"""
        subjects = ["anatomy", "histology", "physiology", "biochemistry"]
        available_subjects = []
        
        # Check which subjects have essay questions
        for subject in subjects:
            subject_essays = get_essay_questions_by_subject(subject)
            if subject_essays:
                available_subjects.append(subject)
        
        if not available_subjects:
            if hasattr(update, 'message'):
                await update.message.reply_text(
                    "❌ No essay questions available at the moment.\n\n"
                    "Please check that essay CSV files are properly configured in the data folder."
                )
            else:
                await update.callback_query.edit_message_text(
                    "❌ No essay questions available at the moment.\n\n"
                    "Please check that essay CSV files are properly configured in the data folder."
                )
            return
        
        keyboard = []
        for subject in available_subjects:
            subject_display = subject.title()
            keyboard.append([InlineKeyboardButton(
                f"📝 {subject_display} Essays", 
                callback_data=f"essay_subject:{subject}"
            )])
        
        keyboard.append([InlineKeyboardButton("« Back to Main Menu", callback_data="main_menu")])
        
        if hasattr(update, 'message'):
            await update.message.reply_text(
                "📝 Essay Questions by Subject\n\n"
                "Select a subject to practice essay writing. "
                "AI will evaluate your responses based on key medical concepts "
                "and essential terminology.\n\n"
                "✅ Spelling variations accepted for medical terms\n"
                "✅ Focus on key concepts and terminology\n"
                "✅ Detailed AI feedback provided",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await update.callback_query.edit_message_text(
                "📝 Essay Questions by Subject\n\n"
                "Select a subject to practice essay writing. "
                "AI will evaluate your responses based on key medical concepts "
                "and essential terminology.\n\n"
                "✅ Spelling variations accepted for medical terms\n"
                "✅ Focus on key concepts and terminology\n"
                "✅ Detailed AI feedback provided",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    
    async def show_subject_essays(self, update: Update, context: ContextTypes.DEFAULT_TYPE, subject: str):
        """Show available essay questions for a specific subject"""
        query = update.callback_query
        
        subject_essays = get_essay_questions_by_subject(subject)
        
        if not subject_essays:
            await query.edit_message_text(
                f"❌ No essay questions available for {subject.title()}.\n\n"
                f"Please check the {subject}_essays.csv file in the data folder.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("« Back to Subjects", callback_data="essay_main")]
                ])
            )
            return
        
        keyboard = []
        for essay_full_id, essay_data in subject_essays.items():
            essay_id = essay_data['essay_id']
            question_preview = essay_data['question'][:60] + "..." if len(essay_data['question']) > 60 else essay_data['question']
            keyboard.append([InlineKeyboardButton(
                f"Essay {essay_id}: {question_preview}", 
                callback_data=f"start_essay:{essay_full_id}"
            )])
        
        keyboard.append([InlineKeyboardButton("« Back to Subjects", callback_data="essay_main")])
        
        await query.edit_message_text(
            f"📝 {subject.title()} Essay Questions\n\n"
            f"Select an essay question to answer. "
            f"AI will evaluate your response based on {subject.lower()}-specific concepts and essential medical terminology.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def start_essay_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE, essay_full_id: str):
        """Start an essay question"""
        query = update.callback_query
        
        essay_data = ESSAY_QUESTIONS.get(essay_full_id)
        if not essay_data:
            await query.edit_message_text("❌ Essay question not found.")
            return
        
        subject = essay_data['subject']
        essay_id = essay_data['essay_id']
        
        # Store essay context in user_data
        context.user_data.update({
            "current_essay": {
                "full_id": essay_full_id,
                "subject": subject,
                "essay_id": essay_id,
                "question": essay_data['question'],
                "waiting_for_response": True
            },
            "quiz_active": False  # Ensure quiz state is clear
        })
        
        await query.edit_message_text(
            f"📝 {subject.title()} Essay Question {essay_id}\n\n"
            f"**Question:** {essay_data['question']}\n\n"
            f"💡 **Please type your essay response now.**\n\n"
            f"**AI Evaluation Criteria:**\n"
            f"• {subject.title()}-specific concepts (40%)\n"
            f"• Medical terminology usage (30%)\n" 
            f"• Clarity and structure (20%)\n"
            f"• Completeness (10%)\n\n"
            f"✅ Spelling variations accepted for medical terms\n"
            f"✅ Focus on {subject.lower()}-specific concepts\n"
            f"✅ Minimum 100 words recommended\n\n"
            f"Type /cancel to stop.",
            parse_mode="Markdown"
        )
    
    async def handle_essay_response(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle user's essay response and send to AI for grading"""
        user_data = context.user_data
        user_text = update.message.text
        
        if not user_data.get("waiting_for_response"):
            return
        
        essay_data = user_data.get("current_essay")
        if not essay_data:
            return
        
        # Send "grading in progress" message
        grading_msg = await update.message.reply_text(
            f"🔄 AI is evaluating your {essay_data['subject']} essay... This may take a moment."
        )
        
        try:
            # Call n8n essay grading webhook
            payload = {
                "essay_id": essay_data["full_id"],
                "subject": essay_data["subject"],
                "question": essay_data["question"],
                "user_response": user_text,
                "user_id": update.effective_user.id,
                "context": f"medical_education_{essay_data['subject']}"
            }
            
            response = requests.post(
                CONFIG["n8n_essay_webhook"],
                json=payload,
                timeout=45  # Longer timeout for AI processing
            )
            
            if response.status_code == 200:
                result = response.json()
                
                feedback_text = (
                    f"📝 **{essay_data['subject'].title()} Essay Evaluation**\n\n"
                    f"📊 **Score:** {result.get('score', 'N/A')}/10\n\n"
                    f"**📋 Feedback:**\n{result.get('feedback', 'No feedback available.')}\n\n"
                    f"**🔑 Key Concepts:**\n{result.get('key_concepts', 'N/A')}\n\n"
                    f"**💡 Suggestions:**\n{result.get('suggestions', 'N/A')}\n\n"
                    f"**📝 Essential Terms Identified:**\n{result.get('essential_terms', 'N/A')}"
                )
                
                # Save essay result to database
                self.db.save_essay_progress(
                    user_id=update.effective_user.id,
                    essay_id=essay_data["full_id"],
                    question=essay_data["question"],
                    user_response=user_text,
                    score=result.get('score', 0),
                    feedback=result.get('feedback', ''),
                    key_concepts=result.get('key_concepts', ''),
                    essential_terms=result.get('essential_terms', '')
                )
                
            else:
                feedback_text = (
                    f"❌ Error evaluating {essay_data['subject']} essay. The AI service may be unavailable.\n\n"
                    "Please try again later or use /start to return to the main menu."
                )
                
        except requests.exceptions.Timeout:
            feedback_text = "⏰ Essay evaluation timed out. Please try again with a shorter response."
        except Exception as e:
            logger.error(f"Essay grading error: {e}")
            feedback_text = "❌ Error evaluating essay. Please try again."
        
        # Send feedback and clean up
        try:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=grading_msg.message_id
            )
        except Exception as e:
            logger.error(f"Error deleting grading message: {e}")
        
        await update.message.reply_text(feedback_text, parse_mode="Markdown")
        
        # Offer to try another essay from the same subject
        keyboard = [
            [InlineKeyboardButton(
                f"📝 Another {essay_data['subject'].title()} Essay", 
                callback_data=f"essay_subject:{essay_data['subject']}"
            )],
            [InlineKeyboardButton("📚 All Essay Subjects", callback_data="essay_main")],
            [InlineKeyboardButton("🎯 Back to Main Menu", callback_data="main_menu")]
        ]
        
        await update.message.reply_text(
            "What would you like to do next?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
        # Clear essay state
        user_data["waiting_for_response"] = False
        user_data["current_essay"] = None
    
    async def cancel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /cancel command"""
        user_data = context.user_data
        
        # Check if quiz is active
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
        
<<<<<<< Updated upstream
<<<<<<< Updated upstream
        # Check if essay session is active
        elif user_data.get("essay_active"):
            user_data.clear()
            await update.message.reply_text("❌ Essay session cancelled. Use /start to begin a new one.")
        
        # Check if simple essay session is active
        elif user_data.get("simple_essay_active"):
            user_data.clear()
            await update.message.reply_text("❌ Essay session cancelled. Use /start to begin a new one.")
        
        else:
            await update.message.reply_text("ℹ️ No active session to cancel.")

    async def explain_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /explain command for quiz questions"""
        user_data = context.user_data
        
        if not user_data.get("quiz_active"):
            await update.message.reply_text(
                "❌ No active quiz. Start a quiz first using /start\n\n"
                "💡 You can also use /ai <question> for general medical questions."
            )
            return
        
        user_question = ' '.join(context.args) if context.args else "Can you explain this question and the correct answer?"
        
        current_question = user_data.get("current_shuffled")
        subject = user_data.get("subject", "general")
        
        if not current_question:
            await update.message.reply_text("❌ No question to explain. Please answer the current question first.")
            return
        
        explaining_msg = await update.message.reply_text("🤔 AI is analyzing the question using college materials...")
        
        try:
            explanation = await self.ai_manager.explain_question(
                current_question, user_question, subject
            )
            
            await explaining_msg.edit_text(
                f"💡 **AI Explanation:**\n\n{explanation}",
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error in explain command: {e}")
            await explaining_msg.edit_text(
                "❌ Sorry, I couldn't generate an explanation right now. "
                "Please try again or continue with the quiz."
            )
    
    async def ai_chat_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /ai command for general medical questions"""
        if not context.args:
            await update.message.reply_text(
                "🤖 **AI Medical Tutor**\n\n"
                "Ask me any medical question! I'll reference our college materials.\n\n"
                "Examples:\n"
                "• `/ai explain action potentials`\n"
                "• `/ai what is the function of the liver?`\n"
                "• `/ai help me understand muscle contraction`\n\n"
                "I'll search through our college PDFs and lecture notes!",
                parse_mode="Markdown"
            )
            return
        
        user_message = ' '.join(context.args)
        
        # Get context from user data if available
        subject = context.user_data.get("subject", "general")
        chat_context = f"User is studying {subject}. Current activity: {self._get_user_activity(context.user_data)}"
        
        chat_msg = await update.message.reply_text("🧠 AI is searching college materials...")
        
        try:
            response = await self.ai_manager.chat_with_ai(user_message, chat_context, subject)
            
            await chat_msg.edit_text(
                f"🤖 **Medical AI Tutor:**\n\n{response}",
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error in AI chat: {e}")
            await chat_msg.edit_text(
                "❌ Sorry, I'm having trouble accessing the AI right now. "
                "Please try again in a moment."
            )
    
    async def search_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /search command for college materials"""
        if not context.args:
            await update.message.reply_text(
                "🔍 **Search College Materials**\n\n"
                "Search through our college PDFs, lecture notes, and handbooks.\n\n"
                "Usage: `/search <your query>`\n\n"
                "Examples:\n"
                "• `/search synovial joints`\n"
                "• `/search action potential phases`\n"
                "• `/search liver functions`",
                parse_mode="Markdown"
            )
            return
        
        query = ' '.join(context.args)
        subject = context.user_data.get("subject", "anatomy")  # Default to anatomy
        
        search_msg = await update.message.reply_text(f"🔍 Searching college {subject} materials...")
        
        try:
            results = await self.ai_manager.search_college_materials(query, subject)
            await search_msg.edit_text(results, parse_mode="Markdown")
            
        except Exception as e:
            logger.error(f"Error in search: {e}")
            await search_msg.edit_text(
                f"❌ Sorry, I couldn't search the materials right now. "
                f"Please try again later."
            )
    
    async def materials_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /materials command to show available college PDFs"""
        subject = context.user_data.get("subject", "anatomy")
        
        available_subjects = self.ai_manager.get_available_college_subjects()
        
        if not available_subjects:
            await update.message.reply_text(
                "📚 **College Materials**\n\n"
                "No college PDFs have been loaded yet.\n\n"
                "Please contact administrator to add college materials."
            )
            return
        
        materials_text = "📚 **Available College Materials**\n\n"
        
        for subj in available_subjects:
            pdfs = self.ai_manager.get_subject_pdfs(subj)
            materials_text += f"**{subj.title()}:**\n"
            if pdfs:
                for pdf in pdfs:
                    materials_text += f"• {pdf}\n"
            else:
                materials_text += "• No PDFs loaded\n"
            materials_text += "\n"
        
        materials_text += f"\n💡 Use `/search <topic>` to search these materials."
        
        await update.message.reply_text(materials_text, parse_mode="Markdown")
    
    def _get_user_activity(self, user_data: dict) -> str:
        """Get current user activity for context"""
        if user_data.get("quiz_active"):
            return "Taking a quiz"
        elif user_data.get("simple_essay_active"):
            essay_type = user_data.get("essay_type", "essay")
            return f"Answering {essay_type} questions"
        elif user_data.get("essay_active"):
            return "Working on essay questions"
        else:
            return "General studying"
=======
        elif user_data.get("waiting_for_response"):
            user_data.clear()
            await update.message.reply_text("❌ Essay cancelled. Use /essay to start a new one.")
        
        else:
            await update.message.reply_text("ℹ️ No active quiz or essay to cancel.")
>>>>>>> Stashed changes
=======
        elif user_data.get("waiting_for_response"):
            user_data.clear()
            await update.message.reply_text("❌ Essay cancelled. Use /essay to start a new one.")
        
        else:
            await update.message.reply_text("ℹ️ No active quiz or essay to cancel.")
>>>>>>> Stashed changes

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle all callback queries"""
        query = update.callback_query
        
        try:
            await query.answer()
        except BadRequest:
            pass
        
        callback_data = query.data
        
        # Handle AI tutor menu
        if callback_data == "ai_tutor_menu":
            await self.handle_ai_tutor_menu(update, context)
            return
        
        # Handle AI hint requests
        if callback_data.startswith("ai_hint:"):
            await self.simple_essay_manager.handle_ai_hint(update, context, int(callback_data.split(":")[1]))
            return
        
        # Handle simple essay callbacks
        if callback_data in ["start_simple_essay", "cancel_simple_essay"]:
            await self.simple_essay_manager.handle_simple_essay_callback(update, context)
            return
        
        # Handle simple essay type selection
        if callback_data.startswith("simple_essay:"):
            essay_type = callback_data.split(":")[1]
            await self.handle_simple_essay_selection(update, context, essay_type)
            return
        
        # Handle AI quick actions
        if callback_data.startswith("ai_quick:"):
            action = callback_data.split(":")[1]
            await self.handle_ai_quick_action(update, context, action)
            return
        
        try:
            # Handle essay-related callbacks first
            if callback_data == "essay_main":
                await self.show_essay_subjects(update, context)
                return
            elif callback_data.startswith("essay_subject:"):
                subject = callback_data.split(":")[1]
                await self.show_subject_essays(update, context, subject)
                return
            elif callback_data.startswith("start_essay:"):
                essay_full_id = callback_data.split(":")[1]
                await self.start_essay_question(update, context, essay_full_id)
                return
            
            # Handle existing navigation callbacks
            parsed = CallbackManager.parse_callback_data(callback_data)
            if not parsed:
                await query.edit_message_text("❌ Invalid selection.")
                return
            
            if parsed["type"] == "main_menu":
                await self.handle_main_menu(update, context)
            elif parsed["type"] == "year":
                await self.handle_year_selection(update, context, parsed["year"])
            elif parsed["type"] == "term":
                await self.handle_term_selection(update, context, parsed["year"], parsed["term"])
            elif parsed["type"] == "block":
                await self.handle_block_selection(update, context, parsed["year"], parsed["term"], parsed["block"])
            elif parsed["type"] == "subject":
                await self.handle_subject_selection(update, context, parsed["year"], parsed["term"], parsed["block"], parsed["subject"])
            elif parsed["type"] == "category":
                await self.handle_category_selection(update, context, parsed["year"], parsed["term"], parsed["block"], parsed["subject"], parsed["category"])
            elif parsed["type"] == "subtopic":
                await self.handle_subtopic_selection(update, context, parsed["year"], parsed["term"], parsed["block"], parsed["subject"], parsed["category"], parsed["subtopic"])
            elif parsed["type"] == "essay_category":
                await self.handle_essay_selection(update, context, parsed["year"], parsed["term"], parsed["block"], parsed["subject"], parsed["category"])
                    
        except Exception as e:
            logger.error(f"❌ Error handling callback: {e}")
            await query.edit_message_text("❌ An error occurred. Please use /start to begin again.")
<<<<<<< Updated upstream
<<<<<<< Updated upstream

    async def handle_ai_tutor_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle AI tutor menu"""
        query = update.callback_query
        
        keyboard = [
            [InlineKeyboardButton("💡 Ask Medical Question", callback_data="ai_quick:question")],
            [InlineKeyboardButton("🔍 Search Materials", callback_data="ai_quick:search")],
            [InlineKeyboardButton("📚 Available Materials", callback_data="ai_quick:materials")],
            [InlineKeyboardButton("📖 Back to Main Menu", callback_data="main_menu")]
        ]
        
        try:
            await query.edit_message_text(
                "🤖 **AI Medical Tutor**\n\n"
                "I can help you with:\n"
                "• Explaining medical concepts\n"
                "• Answering questions using college materials\n"
                "• Searching through PDFs and lecture notes\n"
                "• Providing study guidance\n\n"
                "Choose an option below or use commands:\n"
                "• `/ai <question>` - Ask anything\n"
                "• `/search <topic>` - Search materials\n"
                "• `/materials` - Show available PDFs",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except BadRequest:
            pass

    async def handle_ai_quick_action(self, update: Update, context: ContextTypes.DEFAULT_TYPE, action: str):
        """Handle AI quick actions"""
        query = update.callback_query
        
        if action == "question":
            await query.edit_message_text(
                "💡 **Ask a Medical Question**\n\n"
                "Use the command: `/ai <your question>`\n\n"
                "Examples:\n"
                "• `/ai explain synaptic transmission`\n"
                "• `/ai what are the functions of the kidney?`\n"
                "• `/ai help me understand ECG waves`\n\n"
                "I'll search through our college materials and provide detailed answers!",
                parse_mode="Markdown"
            )
        elif action == "search":
            await query.edit_message_text(
                "🔍 **Search College Materials**\n\n"
                "Use the command: `/search <topic>`\n\n"
                "Examples:\n"
                "• `/search action potential`\n"
                "• `/search muscle contraction steps`\n"
                "• `/search liver anatomy`\n\n"
                "I'll find relevant content from our college PDFs and lecture notes!",
                parse_mode="Markdown"
            )
        elif action == "materials":
            await self.materials_command(update, context)

    async def handle_essay_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                   year: str, term: str, block: str, subject: str, category: str):
        """Handle essay category selection - show simple essay types"""
        query = update.callback_query
        
        keyboard = [
            [InlineKeyboardButton("📝 List Questions", callback_data=f"simple_essay:list")],
            [InlineKeyboardButton("💡 Brief Explanation", callback_data=f"simple_essay:explain")],
            [InlineKeyboardButton("⚖️ Compare & Contrast", callback_data=f"simple_essay:compare")],
            [InlineKeyboardButton("📚 Define & Describe", callback_data=f"simple_essay:define")],
            [InlineKeyboardButton("« Back to Categories", 
                                callback_data=CallbackManager.create_subject_callback(year, term, block, subject))]
        ]
        
        subject_display = FileManager.get_subject_display_name(year, term, block, subject)
        
        try:
            await query.edit_message_text(
                f"✍️ **Essay Questions - {subject_display}**\n\n"
                "Choose question type:\n"
                "• **List Questions**: Provide 2-4 key points\n"
                "• **Brief Explanation**: Explain concepts in 1-3 sentences\n"
                "• **Compare & Contrast**: Highlight similarities and differences\n"
                "• **Define & Describe**: Define terms with key characteristics\n\n"
                "All answers are evaluated by AI using college materials!",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except BadRequest:
            pass

    async def handle_simple_essay_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, essay_type: str):
        """Handle simple essay type selection"""
        user_data = context.user_data
        
        # Store navigation context
        user_data.update({
            "year": user_data.get("year"),
            "term": user_data.get("term"), 
            "block": user_data.get("block"),
            "subject": user_data.get("subject")
        })
        
        await self.simple_essay_manager.start_essay_session(
            update, context,
            user_data["year"], user_data["term"], user_data["block"], 
            user_data["subject"], essay_type
        )

    async def handle_essay_answer(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle essay answers from users"""
        user_data = context.user_data
        
        # Check if we're waiting for a simple essay answer
        if user_data.get("waiting_for_essay_answer") and user_data.get("simple_essay_active"):
            await self.simple_essay_manager.handle_essay_answer(update, context)
            return
        
        # Check if we're waiting for a regular essay answer
        elif user_data.get("waiting_for_essay_answer") and user_data.get("essay_active"):
            # This would be for the original essay manager
            # await self.essay_manager.handle_essay_answer(update, context)
            pass
        
        else:
            # If not waiting for essay answer, check active sessions
            if user_data.get("quiz_active"):
                await update.message.reply_text(
                    "❌ Please answer the current quiz question first.\n\n"
                    "💡 Use /explain if you need help with the question."
                )
            elif user_data.get("simple_essay_active") or user_data.get("essay_active"):
                await update.message.reply_text(
                    "❌ Please answer the current essay question first.\n\n"
                    "💡 Use the AI hint button or /ai for help."
                )
            else:
                # General message - suggest using AI
                await update.message.reply_text(
                    "💡 Need help with medical concepts?\n\n"
                    "Use `/ai <your question>` to ask our AI tutor!\n"
                    "Or use /start to begin a quiz or essay session.",
                    parse_mode="Markdown"
                )
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes

    async def handle_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle return to main menu - show years"""
        query = update.callback_query
        years = FileManager.list_years()
        
        if not years:
            await query.edit_message_text("❌ No academic years available.")
            return
        
        keyboard = []
        for year in years:
            callback_data = CallbackManager.create_year_callback(year)
            display_name = FileManager.get_year_display_name(year)
            keyboard.append([InlineKeyboardButton(display_name, callback_data=callback_data)])
        
<<<<<<< Updated upstream
<<<<<<< Updated upstream
        # Add AI tutor button
        keyboard.append([InlineKeyboardButton("🤖 AI Medical Tutor", callback_data="ai_tutor_menu")])
=======
        # Add essay button to main menu
        keyboard.append([InlineKeyboardButton("📝 Essay Questions", callback_data="essay_main")])
>>>>>>> Stashed changes
=======
        # Add essay button to main menu
        keyboard.append([InlineKeyboardButton("📝 Essay Questions", callback_data="essay_main")])
>>>>>>> Stashed changes
        
        try:
            await query.edit_message_text(
                "🎓 Select your academic year or try essay questions:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except BadRequest:
            pass
    
    # [Keep all the existing navigation methods unchanged - they remain the same]
    async def handle_year_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, year: str):
        """Handle year selection - show terms"""
        query = update.callback_query
        
        terms = FileManager.list_terms(year)
        
        if not terms:
            await query.edit_message_text(f"❌ No terms available for {FileManager.get_year_display_name(year)}")
            return
        
        keyboard = []
        for term in terms:
            callback_data = CallbackManager.create_term_callback(year, term)
            display_name = FileManager.get_term_display_name(year, term)
            keyboard.append([InlineKeyboardButton(display_name, callback_data=callback_data)])
        
        keyboard.append([InlineKeyboardButton("« Back to Years", callback_data="main_menu")])
        
        try:
            year_display = FileManager.get_year_display_name(year)
            await query.edit_message_text(
                f"{year_display}\nSelect term:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except BadRequest:
            pass
    
    async def handle_term_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, year: str, term: str):
        """Handle term selection - show blocks"""
        query = update.callback_query
        
        blocks = FileManager.list_blocks(year, term)
        
        if not blocks:
            year_display = FileManager.get_year_display_name(year)
            term_display = FileManager.get_term_display_name(year, term)
            await query.edit_message_text(f"❌ No blocks available for {year_display} - {term_display}")
            return
        
        keyboard = []
        for block in blocks:
            callback_data = CallbackManager.create_block_callback(year, term, block)
            display_name = FileManager.get_block_display_name(year, term, block)
            keyboard.append([InlineKeyboardButton(display_name, callback_data=callback_data)])
        
        keyboard.append([InlineKeyboardButton("« Back to Terms", 
                        callback_data=CallbackManager.create_year_callback(year))])
        
        try:
            year_display = FileManager.get_year_display_name(year)
            term_display = FileManager.get_term_display_name(year, term)
            await query.edit_message_text(
                f"{year_display} - {term_display}\nSelect block:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except BadRequest:
            pass
    
    async def handle_block_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, year: str, term: str, block: str):
        """Handle block selection - show subjects"""
        query = update.callback_query
        
        subjects = FileManager.list_subjects(year, term, block)
        
        if not subjects:
            year_display = FileManager.get_year_display_name(year)
            term_display = FileManager.get_term_display_name(year, term)
            block_display = FileManager.get_block_display_name(year, term, block)
            await query.edit_message_text(f"❌ No subjects available for {year_display} - {term_display} - {block_display}")
            return
        
        keyboard = []
        for subject in subjects:
            callback_data = CallbackManager.create_subject_callback(year, term, block, subject)
            display_name = FileManager.get_subject_display_name(year, term, block, subject)
            keyboard.append([InlineKeyboardButton(display_name, callback_data=callback_data)])
        
        keyboard.append([InlineKeyboardButton("« Back to Blocks", 
                        callback_data=CallbackManager.create_term_callback(year, term))])
        
        try:
            year_display = FileManager.get_year_display_name(year)
            term_display = FileManager.get_term_display_name(year, term)
            block_display = FileManager.get_block_display_name(year, term, block)
            await query.edit_message_text(
                f"{year_display} - {term_display} - {block_display}\nSelect subject:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except BadRequest:
            pass
    
    async def handle_subject_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, year: str, term: str, block: str, subject: str):
        """Handle subject selection - show categories including essays"""
        query = update.callback_query
        
        # Store subject in context for AI
        context.user_data["subject"] = subject
        
        categories = FileManager.list_categories(year, term, block, subject)
        
        # Check if simple essay questions exist for this subject
        essay_types = ["list", "explain", "compare", "define"]
        has_simple_essays = False
        for essay_type in essay_types:
            simple_essays = self.simple_essay_manager.load_essay_questions(year, term, block, subject, essay_type)
            if simple_essays:
                has_simple_essays = True
                break
        
        # Add essay category if essays exist
        if has_simple_essays and "essays" not in categories:
            categories.append("essays")
        
        if not categories:
            year_display = FileManager.get_year_display_name(year)
            term_display = FileManager.get_term_display_name(year, term)
            block_display = FileManager.get_block_display_name(year, term, block)
            subject_display = FileManager.get_subject_display_name(year, term, block, subject)
            
            error_msg = (
                f"❌ No categories available for:\n"
                f"📅 {year_display} - {term_display} - {block_display}\n"
                f"📚 {subject_display}\n\n"
                f"💡 This usually means:\n"
                f"• The category directories don't exist\n"
                f"• Directory names don't match config\n"
                f"• Check console for debugging output"
            )
            await query.edit_message_text(error_msg)
            return
        
        keyboard = []
        for category in categories:
            if category == "essays":
                # Essay category - use special callback
                callback_data = CallbackManager.create_essay_callback(year, term, block, subject, category)
                display_name = "✍️ Essay Questions (AI Evaluated)"
            else:
                callback_data = CallbackManager.create_category_callback(year, term, block, subject, category)
                display_name = FileManager.get_category_display_name(year, term, block, subject, category)
            
            keyboard.append([InlineKeyboardButton(display_name, callback_data=callback_data)])
        
        # Add AI help button for this subject
        keyboard.append([InlineKeyboardButton("🤖 AI Help for " + subject.title(), callback_data="ai_tutor_menu")])
        
        keyboard.append([InlineKeyboardButton("« Back to Subjects", 
                        callback_data=CallbackManager.create_block_callback(year, term, block))])
        
        try:
            year_display = FileManager.get_year_display_name(year)
            term_display = FileManager.get_term_display_name(year, term)
            block_display = FileManager.get_block_display_name(year, term, block)
            subject_display = FileManager.get_subject_display_name(year, term, block, subject)
            await query.edit_message_text(
                f"{year_display} - {term_display} - {block_display} - {subject_display}\nSelect category:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except BadRequest:
            pass
    
    async def handle_category_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, year: str, term: str, block: str, subject: str, category: str):
        """Handle category selection - show subtopics or start essays"""
        query = update.callback_query
        
        # Store navigation context
        context.user_data.update({
            "year": year,
            "term": term, 
            "block": block,
            "subject": subject,
            "category": category
        })
        
        # If this is an essay category, show essay types
        if category == "essays":
            await self.handle_essay_selection(update, context, year, term, block, subject, category)
            return
        
        # Otherwise show normal subtopics for quizzes
        subtopics = FileManager.list_subtopics(year, term, block, subject, category)
        
        if not subtopics:
            year_display = FileManager.get_year_display_name(year)
            term_display = FileManager.get_term_display_name(year, term)
            block_display = FileManager.get_block_display_name(year, term, block)
            subject_display = FileManager.get_subject_display_name(year, term, block, subject)
            category_display = FileManager.get_category_display_name(year, term, block, subject, category)
            
            error_msg = (
                f"❌ No quizzes available for:\n"
                f"📅 {year_display} - {term_display} - {block_display}\n"
                f"📚 {subject_display} - {category_display}\n\n"
                f"💡 This usually means:\n"
                f"• No CSV files in the category directory\n"
                f"• CSV file names don't match config\n"
                f"• Check console for debugging output"
            )
            await query.edit_message_text(error_msg)
            return
        
        keyboard = []
        for subtopic in subtopics:
            callback_data = CallbackManager.create_subtopic_callback(year, term, block, subject, category, subtopic)
            display_name = FileManager.get_subtopic_display_name(year, term, block, subject, category, subtopic)
            keyboard.append([InlineKeyboardButton(display_name, callback_data=callback_data)])
        
        # Add AI help for this category
        keyboard.append([InlineKeyboardButton("🤖 AI Help for " + category.title(), callback_data="ai_tutor_menu")])
        
        keyboard.append([InlineKeyboardButton("« Back to Categories", 
                        callback_data=CallbackManager.create_subject_callback(year, term, block, subject))])
        
        try:
            year_display = FileManager.get_year_display_name(year)
            term_display = FileManager.get_term_display_name(year, term)
            block_display = FileManager.get_block_display_name(year, term, block)
            subject_display = FileManager.get_subject_display_name(year, term, block, subject)
            category_display = FileManager.get_category_display_name(year, term, block, subject, category)
            await query.edit_message_text(
                f"{year_display} - {term_display} - {block_display} - {subject_display} - {category_display}\nSelect quiz:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except BadRequest:
            pass
    
    async def handle_subtopic_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, year: str, term: str, block: str, subject: str, category: str, subtopic: str):
        """Handle subtopic selection and start quiz"""
        await self.quiz_manager.start_quiz(update, context, year, term, block, subject, category, subtopic)
    
    async def handle_poll_answer(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle poll answers"""
        await self.quiz_manager.handle_poll_answer(update, context)
    
    def register_handlers(self, application):
        """Register all handlers with the application"""
        # Command handlers
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("stats", self.stats_command))
        application.add_handler(CommandHandler("essay", self.essay_command))
        application.add_handler(CommandHandler("cancel", self.cancel_command))
<<<<<<< Updated upstream
<<<<<<< Updated upstream
        application.add_handler(CommandHandler("explain", self.explain_command))
        application.add_handler(CommandHandler("ai", self.ai_chat_command))
        application.add_handler(CommandHandler("search", self.search_command))
        application.add_handler(CommandHandler("materials", self.materials_command))
        
        # Callback query handler - must be before MessageHandler to catch callbacks first
        application.add_handler(CallbackQueryHandler(self.handle_callback))
        
        # Poll answer handler
        application.add_handler(PollAnswerHandler(self.handle_poll_answer))
        
        # Message handler for essay answers - must be last to not interfere with other handlers
        application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, 
            self.handle_essay_answer
=======
        
        application.add_handler(CallbackQueryHandler(self.handle_callback))
=======
        
        application.add_handler(CallbackQueryHandler(self.handle_callback))
>>>>>>> Stashed changes
        application.add_handler(PollAnswerHandler(self.handle_poll_answer))
        
        # Add message handler for essay responses (must be after command handlers)
        application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, 
            self.handle_essay_response
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
        ))