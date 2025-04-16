import logging
from collections import defaultdict
import threading

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# In-memory database
# Using dictionaries to store the data instead of a real database for simplicity
# Structure:
# active_topics = {(chat_id, topic_id): True/False}
# user_languages = {user_id: language_code}
# user_chat_mapping = {(user_id, chat_id): True}
active_topics = {}
user_languages = {}
user_chat_mapping = {}

# Thread lock for thread safety
lock = threading.RLock()

def activate_topic(chat_id, topic_id=0):
    """
    Activate translation bot for a specific topic in a chat.
    
    Args:
        chat_id (int): The chat ID
        topic_id (int, optional): The topic ID. Defaults to 0 for regular groups.
    """
    with lock:
        active_topics[(chat_id, topic_id)] = True
        logger.info(f"Activated topic {topic_id} in chat {chat_id}")

def deactivate_topic(chat_id, topic_id=0):
    """
    Deactivate translation bot for a specific topic in a chat.
    
    Args:
        chat_id (int): The chat ID
        topic_id (int, optional): The topic ID. Defaults to 0 for regular groups.
    """
    with lock:
        active_topics[(chat_id, topic_id)] = False
        logger.info(f"Deactivated topic {topic_id} in chat {chat_id}")

def is_topic_active(chat_id, topic_id=0):
    """
    Check if the translation bot is active for a specific topic in a chat.
    
    Args:
        chat_id (int): The chat ID
        topic_id (int, optional): The topic ID. Defaults to 0 for regular groups.
        
    Returns:
        bool: True if active, False otherwise
    """
    with lock:
        return active_topics.get((chat_id, topic_id), False)

def set_user_language(user_id, language_code):
    """
    Set a user's preferred language.
    
    Args:
        user_id (int): The user ID
        language_code (str): The ISO language code
    """
    with lock:
        user_languages[user_id] = language_code
        logger.info(f"Set language for user {user_id} to {language_code}")

def get_user_language(user_id):
    """
    Get a user's preferred language.
    
    Args:
        user_id (int): The user ID
        
    Returns:
        str: The user's language code or None if not set
    """
    with lock:
        return user_languages.get(user_id)

def register_user_in_chat(user_id, chat_id):
    """
    Register that a user is in a specific chat.
    
    Args:
        user_id (int): The user ID
        chat_id (int): The chat ID
    """
    with lock:
        user_chat_mapping[(user_id, chat_id)] = True
        logger.debug(f"Registered user {user_id} in chat {chat_id}")

def get_all_users_languages_in_chat(chat_id):
    """
    Get all users' languages in a specific chat.
    
    Args:
        chat_id (int): The chat ID
        
    Returns:
        dict: A dictionary of {user_id: language_code}
    """
    with lock:
        result = {}
        for (uid, cid), active in user_chat_mapping.items():
            if cid == chat_id and active:
                lang = user_languages.get(uid)
                if lang:
                    result[uid] = lang
        return result
