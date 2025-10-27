"""
Bot command and callback handlers
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, CommandHandler, PollAnswerHandler
from telegram.error import BadRequest

from file_manager import FileManager
from callback_manager import CallbackManager
from quiz_manager import QuizManager
from database import DatabaseManager

logger = logging.getLogger(__name__)

class BotHandlers:
    def __init__(self, database: DatabaseManager, quiz_manager: QuizManager):
        self.db = database
        self.quiz_manager = quiz_manager
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        self.db.update_user(user.id, user.username, user.first_name, user.last_name)
        
        context.user_data.clear()
        topics = FileManager.list_topics()
        
        if not topics:
            await update.message.reply_text("📝 No quiz topics available.")
            return
        
        keyboard = []
        for topic in topics:
            callback_data = CallbackManager.create_topic_callback(topic)
            display_name = FileManager.get_topic_display_name(topic)
            keyboard.append([InlineKeyboardButton(display_name, callback_data=callback_data)])
        
        await update.message.reply_text(
            "🎯 Welcome to Quiz Bot!\n\nSelect a subject to begin:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = (
            "🤖 Quiz Bot Help\n\n"
            "📚 Available Commands:\n"
            "• /start - Start the bot and select quiz\n"
            "• /stats - View your quiz statistics\n"
            "• /cancel - Cancel current quiz\n"
            "• /help - Show this help message\n\n"
            "🎯 How to Use:\n"
            "1. Use /start to begin\n"
            "2. Select a subject and topic\n"
            "3. Answer questions at your own pace\n"
            "4. View your results at the end"
        )
        
        await update.message.reply_text(help_text)
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command"""
        user = update.effective_user
        stats = self.db.get_user_stats(user.id)
        
        if stats['total_quizzes'] == 0:
            await update.message.reply_text("📊 You haven't completed any quizzes yet!")
            return
        
        stats_text = (
            f"📊 Your Quiz Statistics\n\n"
            f"• Total Quizzes: {stats['total_quizzes']}\n"
            f"• Average Score: {stats['average_score']}%\n\n"
            f"Keep up the great work! 🎯"
        )
        
        await update.message.reply_text(stats_text)
    
    async def cancel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle all callback queries"""
        query = update.callback_query
        
        try:
            await query.answer()
        except BadRequest:
            pass  # Ignore expired queries
        
        callback_data = query.data
        logger.info(f"📨 Received callback: {callback_data}")
        
        try:
            parsed = CallbackManager.parse_callback_data(callback_data)
            if not parsed:
                await query.edit_message_text("❌ Invalid selection. Please use /start to begin again.")
                return
            
            if parsed["type"] == "main_menu":
                await self.handle_main_menu(update, context)
            elif parsed["type"] == "topic":
                await self.handle_topic_selection(update, context, parsed["topic"])
            elif parsed["type"] == "subtopic":
                await self.handle_subtopic_selection(update, context, parsed["topic"], parsed["subtopic"])
                    
        except Exception as e:
            logger.error(f"❌ Error handling callback: {e}")
            await query.edit_message_text("❌ An error occurred. Please try again.")

    async def handle_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle return to main menu"""
        query = update.callback_query
        topics = FileManager.list_topics()
        
        if not topics:
            await query.edit_message_text("❌ No topics available.")
            return
        
        keyboard = []
        for topic in topics:
            callback_data = CallbackManager.create_topic_callback(topic)
            display_name = FileManager.get_topic_display_name(topic)
            keyboard.append([InlineKeyboardButton(display_name, callback_data=callback_data)])
        
        try:
            await query.edit_message_text(
                "📚 Select a subject:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except BadRequest as e:
            if "message is not modified" not in str(e).lower():
                raise e

    async def handle_topic_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, topic: str):
        """Handle topic selection"""
        query = update.callback_query
        
        subtopics = FileManager.list_subtopics(topic)
        
        if not subtopics:
            topic_display = FileManager.get_topic_display_name(topic)
            await query.edit_message_text(f"❌ No quizzes available for {topic_display}")
            return
        
        keyboard = []
        for subtopic in subtopics:
            callback_data = CallbackManager.create_subtopic_callback(topic, subtopic)
            display_name = FileManager.get_subtopic_display_name(topic, subtopic)
            keyboard.append([InlineKeyboardButton(display_name, callback_data=callback_data)])
        
        keyboard.append([InlineKeyboardButton("« Back to Subjects", callback_data="main_menu")])
        
        try:
            topic_display = FileManager.get_topic_display_name(topic)
            await query.edit_message_text(
                f"{topic_display} - Choose a topic:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except BadRequest as e:
            if "message is not modified" not in str(e).lower():
                raise e

    async def handle_subtopic_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, topic: str, subtopic: str):
        """Handle subtopic selection and start quiz"""
        await self.quiz_manager.start_quiz(update, context, topic, subtopic)
    
    async def handle_poll_answer(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle poll answers"""
        await self.quiz_manager.handle_poll_answer(update, context)
    
    def register_handlers(self, application):
        """Register all handlers with the application"""
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("stats", self.stats_command))
        application.add_handler(CommandHandler("cancel", self.cancel_command))
        application.add_handler(CallbackQueryHandler(self.handle_callback))
        # FIXED: Use PollAnswerHandler instead of CallbackQueryHandler
        application.add_handler(PollAnswerHandler(self.handle_poll_answer))