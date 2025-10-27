"""
Bot command and callback handlers for nested structure
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
    
    # ... (keep other command handlers: help_command, stats_command, cancel_command the same)
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle all callback queries"""
        query = update.callback_query
        
        try:
            await query.answer()
        except BadRequest:
            pass
        
        callback_data = query.data
        
        try:
            parsed = CallbackManager.parse_callback_data(callback_data)
            if not parsed:
                await query.edit_message_text("❌ Invalid selection.")
                return
            
            if parsed["type"] == "main_menu":
                await self.handle_main_menu(update, context)
            elif parsed["type"] == "topic":
                await self.handle_topic_selection(update, context, parsed["topic"])
            elif parsed["type"] == "category":
                await self.handle_category_selection(update, context, parsed["topic"], parsed["category"])
            elif parsed["type"] == "subtopic":
                await self.handle_subtopic_selection(update, context, parsed["topic"], parsed["category"], parsed["subtopic"])
                    
        except Exception as e:
            logger.error(f"❌ Error handling callback: {e}")
            await query.edit_message_text("❌ An error occurred.")
    
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
        except BadRequest:
            pass
    
    async def handle_topic_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, topic: str):
        """Handle topic selection - show categories"""
        query = update.callback_query
        
        categories = FileManager.list_categories(topic)
        
        if not categories:
            await query.edit_message_text(f"❌ No categories available for {FileManager.get_topic_display_name(topic)}")
            return
        
        keyboard = []
        for category in categories:
            callback_data = CallbackManager.create_category_callback(topic, category)
            display_name = FileManager.get_category_display_name(topic, category)
            keyboard.append([InlineKeyboardButton(display_name, callback_data=callback_data)])
        
        keyboard.append([InlineKeyboardButton("« Back to Subjects", callback_data="main_menu")])
        
        try:
            topic_display = FileManager.get_topic_display_name(topic)
            await query.edit_message_text(
                f"{topic_display} - Choose a category:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except BadRequest:
            pass
    
    async def handle_category_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, topic: str, category: str):
        """Handle category selection - show subtopics"""
        query = update.callback_query
        
        subtopics = FileManager.list_subtopics(topic, category)
        
        if not subtopics:
            topic_display = FileManager.get_topic_display_name(topic)
            category_display = FileManager.get_category_display_name(topic, category)
            await query.edit_message_text(f"❌ No quizzes available for {topic_display} - {category_display}")
            return
        
        keyboard = []
        for subtopic in subtopics:
            callback_data = CallbackManager.create_subtopic_callback(topic, category, subtopic)
            display_name = FileManager.get_subtopic_display_name(topic, category, subtopic)
            keyboard.append([InlineKeyboardButton(display_name, callback_data=callback_data)])
        
        keyboard.append([InlineKeyboardButton("« Back to Categories", 
                        callback_data=CallbackManager.create_topic_callback(topic))])
        
        try:
            topic_display = FileManager.get_topic_display_name(topic)
            category_display = FileManager.get_category_display_name(topic, category)
            await query.edit_message_text(
                f"{topic_display} - {category_display}\nChoose a topic:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except BadRequest:
            pass
    
    async def handle_subtopic_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, topic: str, category: str, subtopic: str):
        """Handle subtopic selection and start quiz"""
        await self.quiz_manager.start_quiz(update, context, topic, category, subtopic)
    
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
        application.add_handler(PollAnswerHandler(self.handle_poll_answer))