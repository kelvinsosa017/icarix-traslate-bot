import logging
from sqlalchemy.exc import SQLAlchemyError
from models import Session, ActiveTopic, UserLanguage, UserChatMapping, create_tables

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Asegurarse de que las tablas existan
create_tables()

def activate_topic(chat_id, topic_id=0):
    """
    Activate translation bot for a specific topic in a chat.
    
    Args:
        chat_id (int): The chat ID
        topic_id (int, optional): The topic ID. Defaults to 0 for regular groups.
    """
    session = Session()
    try:
        # Buscar si ya existe un registro para este chat y tema
        active_topic = session.query(ActiveTopic).filter_by(
            chat_id=chat_id, topic_id=topic_id
        ).first()
        
        if active_topic:
            # Si existe, activarlo
            active_topic.is_active = True
        else:
            # Si no existe, crear uno nuevo
            active_topic = ActiveTopic(
                chat_id=chat_id,
                topic_id=topic_id,
                is_active=True
            )
            session.add(active_topic)
            
        session.commit()
        logger.info(f"Activated topic {topic_id} in chat {chat_id}")
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Database error activating topic: {e}")
    finally:
        session.close()

def deactivate_topic(chat_id, topic_id=0):
    """
    Deactivate translation bot for a specific topic in a chat.
    
    Args:
        chat_id (int): The chat ID
        topic_id (int, optional): The topic ID. Defaults to 0 for regular groups.
    """
    session = Session()
    try:
        # Buscar si ya existe un registro para este chat y tema
        active_topic = session.query(ActiveTopic).filter_by(
            chat_id=chat_id, topic_id=topic_id
        ).first()
        
        if active_topic:
            # Si existe, desactivarlo
            active_topic.is_active = False
            session.commit()
            logger.info(f"Deactivated topic {topic_id} in chat {chat_id}")
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Database error deactivating topic: {e}")
    finally:
        session.close()

def is_topic_active(chat_id, topic_id=0):
    """
    Check if the translation bot is active for a specific topic in a chat.
    
    Args:
        chat_id (int): The chat ID
        topic_id (int, optional): The topic ID. Defaults to 0 for regular groups.
        
    Returns:
        bool: True if active, False otherwise
    """
    session = Session()
    try:
        # Buscar si existe un registro activo para este chat y tema
        active_topic = session.query(ActiveTopic).filter_by(
            chat_id=chat_id, topic_id=topic_id, is_active=True
        ).first()
        
        return active_topic is not None
    except SQLAlchemyError as e:
        logger.error(f"Database error checking topic activity: {e}")
        return False
    finally:
        session.close()

def set_user_language(user_id, language_code):
    """
    Set a user's preferred language.
    
    Args:
        user_id (int): The user ID
        language_code (str): The ISO language code
    """
    session = Session()
    try:
        # Buscar si ya existe un registro para este usuario
        user_language = session.query(UserLanguage).filter_by(
            user_id=user_id
        ).first()
        
        if user_language:
            # Si existe, actualizar el idioma
            user_language.language_code = language_code
        else:
            # Si no existe, crear uno nuevo
            user_language = UserLanguage(
                user_id=user_id,
                language_code=language_code
            )
            session.add(user_language)
            
        session.commit()
        logger.info(f"Set language for user {user_id} to {language_code}")
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Database error setting user language: {e}")
    finally:
        session.close()

def get_user_language(user_id):
    """
    Get a user's preferred language.
    
    Args:
        user_id (int): The user ID
        
    Returns:
        str: The user's language code or None if not set
    """
    session = Session()
    try:
        # Buscar el idioma del usuario
        user_language = session.query(UserLanguage).filter_by(
            user_id=user_id
        ).first()
        
        return user_language.language_code if user_language else None
    except SQLAlchemyError as e:
        logger.error(f"Database error getting user language: {e}")
        return None
    finally:
        session.close()

def register_user_in_chat(user_id, chat_id):
    """
    Register that a user is in a specific chat.
    
    Args:
        user_id (int): The user ID
        chat_id (int): The chat ID
    """
    session = Session()
    try:
        # Buscar si ya existe un registro para este usuario y chat
        user_chat = session.query(UserChatMapping).filter_by(
            user_id=user_id, chat_id=chat_id
        ).first()
        
        if not user_chat:
            # Si no existe, crear uno nuevo
            user_chat = UserChatMapping(
                user_id=user_id,
                chat_id=chat_id
            )
            session.add(user_chat)
            session.commit()
            logger.debug(f"Registered user {user_id} in chat {chat_id}")
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Database error registering user in chat: {e}")
    finally:
        session.close()

def get_all_users_languages_in_chat(chat_id):
    """
    Get all users' languages in a specific chat.
    
    Args:
        chat_id (int): The chat ID
        
    Returns:
        dict: A dictionary of {user_id: language_code}
    """
    session = Session()
    try:
        # Obtener todos los usuarios en este chat
        user_chats = session.query(UserChatMapping).filter_by(
            chat_id=chat_id
        ).all()
        
        result = {}
        for user_chat in user_chats:
            # Para cada usuario, obtener su idioma
            user_language = session.query(UserLanguage).filter_by(
                user_id=user_chat.user_id
            ).first()
            
            if user_language:
                result[user_chat.user_id] = user_language.language_code
                
        return result
    except SQLAlchemyError as e:
        logger.error(f"Database error getting users languages in chat: {e}")
        return {}
    finally:
        session.close()
