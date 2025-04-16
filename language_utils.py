import os
import logging
from langdetect import detect, LangDetectException
from deep_translator import GoogleTranslator

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Dictionary mapping common language codes to their full names
LANGUAGE_NAMES = {
    'en': 'English', 'es': 'Spanish', 'fr': 'French', 'de': 'German', 
    'it': 'Italian', 'pt': 'Portuguese', 'nl': 'Dutch', 'ru': 'Russian',
    'ja': 'Japanese', 'ko': 'Korean', 'zh': 'Chinese', 'ar': 'Arabic',
    'hi': 'Hindi', 'bn': 'Bengali', 'pa': 'Punjabi', 'te': 'Telugu',
    'mr': 'Marathi', 'ta': 'Tamil', 'ur': 'Urdu', 'fa': 'Persian',
    'tr': 'Turkish', 'pl': 'Polish', 'uk': 'Ukrainian', 'vi': 'Vietnamese',
    'th': 'Thai', 'id': 'Indonesian', 'ms': 'Malay', 'el': 'Greek',
    'cs': 'Czech', 'da': 'Danish', 'fi': 'Finnish', 'no': 'Norwegian',
    'sv': 'Swedish', 'ro': 'Romanian', 'hu': 'Hungarian', 'bg': 'Bulgarian',
    'he': 'Hebrew', 'af': 'Afrikaans', 'sw': 'Swahili', 'tl': 'Tagalog'
}

def detect_language(text):
    """
    Detect the language of a text using langdetect.
    
    Args:
        text (str): The text to detect language from
        
    Returns:
        str: The detected language code or None if detection fails
    """
    try:
        # Detect language only if the text has a meaningful length
        if len(text) > 5:
            detected = detect(text)
            logger.debug(f"Detected language: {detected} for text: {text[:20]}...")
            return detected
    except LangDetectException as e:
        logger.warning(f"Language detection failed: {e}")
    
    return None

def translate_text(text, target_lang='en', source_lang=None):
    """
    Translate text using GoogleTranslator from deep_translator.
    
    Args:
        text (str): The text to translate
        target_lang (str): The target language code
        source_lang (str, optional): The source language code
        
    Returns:
        str: The translated text or None if translation fails
    """
    if not text or not target_lang:
        return None
    
    try:
        # Set up the translator
        if source_lang:
            translator = GoogleTranslator(source=source_lang, target=target_lang)
        else:
            translator = GoogleTranslator(target=target_lang)
        
        # Translate the text
        translated_text = translator.translate(text)
        
        # Log the translation
        source_display = source_lang if source_lang else "auto"
        logger.debug(f"Translated from {source_display} to {target_lang}: {text[:20]}... -> {translated_text[:20]}...")
        
        return translated_text
    
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return None

def is_valid_language_code(language_code):
    """
    Check if a language code is valid.
    
    Args:
        language_code (str): The language code to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        # Check if the language code is in the list of language names
        return language_code in LANGUAGE_NAMES
    except Exception as e:
        logger.error(f"Error validating language code: {e}")
        return False

def get_language_name(language_code):
    """
    Get the full name of a language from its code.
    
    Args:
        language_code (str): The language code
        
    Returns:
        str: The full language name or the code if not found
    """
    return LANGUAGE_NAMES.get(language_code, language_code)
