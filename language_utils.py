import logging
from deep_translator import GoogleTranslator
from langdetect import detect, LangDetectException
import iso639

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def detect_language(text):
    """
    Detect the language of a text using langdetect.
    
    Args:
        text (str): The text to detect language from
        
    Returns:
        str: The detected language code or 'en' if detection fails
    """
    if not text or len(text.strip()) < 5:
        return 'en'
        
    try:
        return detect(text)
    except LangDetectException as e:
        logger.warning(f"Language detection failed: {e}")
        return 'en'

def translate_text(text, target_lang='en', source_lang=None):
    """
    Translate text using GoogleTranslator from deep_translator.
    
    Args:
        text (str): The text to translate
        target_lang (str): The target language code
        source_lang (str, optional): The source language code
        
    Returns:
        str: The translated text or error message if translation fails
    """
    try:
        # Si el idioma de origen no se especifica, usar 'auto'
        src = source_lang if source_lang else 'auto'
        
        return GoogleTranslator(source=src, target=target_lang).translate(text)
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return "[Error en traducción]"

def is_valid_language_code(language_code):
    """
    Check if a language code is valid.
    
    Args:
        language_code (str): The language code to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        # Try to get language from ISO code
        iso639.languages.get(part1=language_code)
        return True
    except KeyError:
        try:
            # Try as a 3-letter code
            iso639.languages.get(part2b=language_code)
            return True
        except KeyError:
            try:
                # Try as a bibliographic code
                iso639.languages.get(part2t=language_code)
                return True
            except KeyError:
                return False

def get_language_name(language_code):
    """
    Get the full name of a language from its code.
    
    Args:
        language_code (str): The language code
        
    Returns:
        str: The full language name or the code if not found
    """
    try:
        return iso639.languages.get(part1=language_code).name
    except KeyError:
        try:
            return iso639.languages.get(part2b=language_code).name
        except KeyError:
            try:
                return iso639.languages.get(part2t=language_code).name
            except KeyError:
                return language_code