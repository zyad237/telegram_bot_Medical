"""
Bot command and callback handlers for 6-level navigation
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
        
        await update.message.reply_text(
            "🎓 Medical Quiz Bot\n\nSelect your academic year:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    # ... (keep help_command, stats_command, cancel_command the same)
    
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
                    
        except Exception as e:
            logger.error(f"❌ Error handling callback: {e}")
            await query.edit_message_text("❌ An error occurred.")

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
        
        try:
            await query.edit_message_text(
                "🎓 Select your academic year:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except BadRequest:
            pass
    
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
        """Handle subject selection - show categories"""
        query = update.callback_query
        
        categories = FileManager.list_categories(year, term, block, subject)
        
        if not categories:
            year_display = FileManager.get_year_display_name(year)
            term_display = FileManager.get_term_display_name(year, term)
            block_display = FileManager.get_block_display_name(year, term, block)
            subject_display = FileManager.get_subject_display_name(year, term, block, subject)
            await query.edit_message_text(f"❌ No categories available for {year_display} - {term_display} - {block_display} - {subject_display}")
            return
        
        keyboard = []
        for category in categories:
            callback_data = CallbackManager.create_category_callback(year, term, block, subject, category)
            display_name = FileManager.get_category_display_name(year, term, block, subject, category)
            keyboard.append([InlineKeyboardButton(display_name, callback_data=callback_data)])
        
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
        """Handle category selection - show subtopics"""
        query = update.callback_query
        
        subtopics = FileManager.list_subtopics(year, term, block, subject, category)
        
        if not subtopics:
            year_display = FileManager.get_year_display_name(year)
            term_display = FileManager.get_term_display_name(year, term)
            block_display = FileManager.get_block_display_name(year, term, block)
            subject_display = FileManager.get_subject_display_name(year, term, block, subject)
            category_display = FileManager.get_category_display_name(year, term, block, subject, category)
            await query.edit_message_text(f"❌ No quizzes available for {year_display} - {term_display} - {block_display} - {subject_display} - {category_display}")
            return
        
        keyboard = []
        for subtopic in subtopics:
            callback_data = CallbackManager.create_subtopic_callback(year, term, block, subject, category, subtopic)
            display_name = FileManager.get_subtopic_display_name(year, term, block, subject, category, subtopic)
            keyboard.append([InlineKeyboardButton(display_name, callback_data=callback_data)])
        
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
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("stats", self.stats_command))
        application.add_handler(CommandHandler("cancel", self.cancel_command))
        application.add_handler(CallbackQueryHandler(self.handle_callback))
        application.add_handler(PollAnswerHandler(self.handle_poll_answer))