# Bot de Telegram para traducción automática
import os
import logging
import html
from telegram import Update, Chat, BotCommand, ParseMode
from telegram.ext import (Updater, CommandHandler, MessageHandler,
                         CallbackContext, Filters, Dispatcher)
import database
import language_utils

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get bot token from environment variables
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8128964123:AAHf0vLSgUmmN_3QIzzI6Gqem8-Zg9sTmQE")


# Commands
def start_command(update: Update, context: CallbackContext) -> None:
    """
    Start command to activate the bot in a specific topic.
    Only admins can use this command.
    """
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    
    # Check if the message is in a group
    if chat.type not in [Chat.GROUP, Chat.SUPERGROUP]:
        message.reply_text("This bot is designed for group chats. Please add me to a group!")
        return
    
    # Check if the user is an admin
    try:
        chat_member = context.bot.get_chat_member(chat.id, user.id)
        is_admin = chat_member.status in ["creator", "administrator"]
    except Exception as e:
        logger.error(f"Error checking admin status: {e}")
        is_admin = False
    
    if not is_admin:
        message.reply_text("Only group administrators can activate the translation bot.")
        return
    
    # Get the topic ID if available (0 for regular groups)
    topic_id = getattr(message, 'message_thread_id', 0) if hasattr(message, 'is_topic_message') and getattr(message, 'is_topic_message', False) else 0
    
    # Activate the bot for this topic
    database.activate_topic(chat.id, topic_id)
    
    # Register the admin in this chat
    database.register_user_in_chat(user.id, chat.id)
    
    topic_str = f"topic #{topic_id}" if topic_id else "this group"
    message.reply_text(
        f"✅ Translation bot activated in {topic_str}!\n\n"
        f"I'll automatically translate messages between users who speak different languages.\n\n"
        f"Users don't need to do anything special - I'll detect their language from their messages "
        f"and translate accordingly."
    )


def help_command(update: Update, context: CallbackContext) -> None:
    """Show help information about the bot."""
    help_text = (
        "🌍 *Icarix Translator Bot* 🌍\n\n"
        "I automatically translate messages between users who speak different languages in group chats.\n\n"
        "*Commands:*\n"
        "/start - Activate the bot in a specific topic (admin only)\n"
        "/help - Show this help message\n"
        "/language [code] - Manually set your language (e.g., /language es)\n\n"
        "*How it works:*\n"
        "1. An admin activates me in a topic using /start\n"
        "2. I detect each user's language automatically\n"
        "3. I translate messages between users who speak different languages\n"
        "4. Translations are only visible to the recipients who need them\n\n"
        "*Supported Languages:*\n"
        "I support over 100 languages through Google Translate."
    )
    update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)


def language_command(update: Update, context: CallbackContext) -> None:
    """
    Command to manually set a user's preferred language.
    Usage: /language [language_code]
    """
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    # Check if language code was provided
    if not context.args:
        update.message.reply_text(
            "Please specify a language code. For example:\n"
            "/language en - for English\n"
            "/language es - for Spanish\n"
            "/language fr - for French\n"
            "/language zh - for Chinese\n"
            "See full list of language codes: https://cloud.google.com/translate/docs/languages"
        )
        return
    
    language_code = context.args[0].lower()
    
    # Validate language code
    if language_utils.is_valid_language_code(language_code):
        database.set_user_language(user_id, language_code)
        database.register_user_in_chat(user_id, chat_id)
        language_name = language_utils.get_language_name(language_code)
        update.message.reply_text(f"Your language has been set to {language_name} ({language_code}).")
    else:
        update.message.reply_text(
            f"Invalid language code: {language_code}\n"
            "Please use a valid ISO language code like 'en', 'es', 'fr', etc."
        )


def handle_message(update: Update, context: CallbackContext) -> None:
    """Handle incoming messages and translate if necessary."""
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    
    # Ignore commands
    if message.text and message.text.startswith('/'):
        return
    
    # Check if message is empty or has no text content
    if not message.text:
        return
    
    # Ignore messages from bots
    if user.is_bot:
        return
    
    # Get topic ID (0 for regular groups)
    topic_id = getattr(message, 'message_thread_id', 0) if hasattr(message, 'is_topic_message') and getattr(message, 'is_topic_message', False) else 0
    
    # Check if the bot is activated for this topic
    if not database.is_topic_active(chat.id, topic_id):
        return
    
    # Register the user in this chat
    database.register_user_in_chat(user.id, chat.id)
    
    # Get the message text
    text = message.text
    
    # Detect language and update user language in database
    detected_lang = language_utils.detect_language(text)
    if detected_lang:
        database.set_user_language(user.id, detected_lang)
    else:
        # If language detection fails, use the user's previous language or default to English
        detected_lang = database.get_user_language(user.id) or 'en'
    
    # Translate for each user in the chat with a different language
    user_languages = database.get_all_users_languages_in_chat(chat.id)
    
    for recipient_id, recipient_lang in user_languages.items():
        # Skip if recipient is the sender or if languages are the same
        if recipient_id == user.id or recipient_lang == detected_lang:
            continue
        
        # Translate the message
        try:
            translated_text = language_utils.translate_text(text, target_lang=recipient_lang, source_lang=detected_lang)
            
            # If translation is different from original, send it
            if translated_text and translated_text.lower() != text.lower():
                # Format the message with original text and translation
                sender_name = html.escape(user.first_name)
                message_text = (
                    f"<b>🔄 Translated from {language_utils.get_language_name(detected_lang)}:</b>\n"
                    f"{html.escape(translated_text)}"
                )
                
                # Send translation as a reply to the original message
                context.bot.send_message(
                    chat_id=chat.id,
                    text=message_text,
                    reply_to_message_id=message.message_id,
                    parse_mode=ParseMode.HTML
                )
                logger.debug(f"Sent translation from {detected_lang} to {recipient_lang} for user {recipient_id}")
        except Exception as e:
            logger.error(f"Translation error: {e}")


def set_commands(dispatcher: Dispatcher) -> None:
    """Set bot commands."""
    commands = [
        BotCommand("start", "Activate the bot in a topic (admin only)"),
        BotCommand("help", "Show help information"),
        BotCommand("language", "Manually set your language")
    ]
    dispatcher.bot.set_my_commands(commands)
    logger.info("Bot commands set up")


def run_bot():
    """Initialize and run the Telegram bot."""
    logger.info("Initializing bot")
    
    # Create the Updater and pass it your bot's token
    updater = Updater(BOT_TOKEN)
    
    # Delete webhook before starting polling
    updater.bot.delete_webhook()
    
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher
    
    # Register command handlers
    dispatcher.add_handler(CommandHandler("start", start_command))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("language", language_command))
    
    # Register message handler
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    
    # Set bot commands
    set_commands(dispatcher)
    
    # Start the Bot
    logger.info("Starting bot")
    updater.start_polling()
    
    # Run the bot until you press Ctrl-C
    # updater.idle()