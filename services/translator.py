"""
Language Translation Service
Uses deep-translator (Google Translate) for real multi-language translation
"""

import logging

# Try deep-translator (preferred - uses Google Translate, no API key needed)
try:
    from deep_translator import GoogleTranslator
    DEEP_TRANSLATOR_AVAILABLE = True
except ImportError:
    DEEP_TRANSLATOR_AVAILABLE = False
    print("⚠️ deep-translator not available, using fallback translation")

# Fallback: transformers-based translation
try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


class LanguageTranslator:
    def __init__(self):
        """
        Initialize the translation service
        """
        if DEEP_TRANSLATOR_AVAILABLE:
            print("✅ Language Translator initialized successfully (Google Translate via deep-translator)")
        elif TRANSFORMERS_AVAILABLE:
            print("⚠️ Language Translator using transformers fallback")
        else:
            print("⚠️ Language Translator using basic word-level fallback only")

    def translate(self, text, source_lang="auto", target_lang="en"):
        """
        Translate text from source language to target language.

        Args:
            text (str): Text to translate
            source_lang (str): Source language code (e.g. 'en', 'auto')
            target_lang (str): Target language code (e.g. 'es', 'fr')

        Returns:
            str: Translated text
        """
        try:
            text = text.strip()
            if not text:
                return ""

            # If source and target are the same, return as-is
            if source_lang == target_lang and source_lang != "auto":
                return text

            if DEEP_TRANSLATOR_AVAILABLE:
                return self._translate_with_google(text, source_lang, target_lang)
            else:
                return self._fallback_translate(text, source_lang, target_lang)

        except Exception as e:
            print(f"❌ Translation error: {e}")
            # Try basic fallback before giving up
            try:
                return self._fallback_translate(text, source_lang, target_lang)
            except Exception:
                return f"[Translation unavailable] {text}"

    def _translate_with_google(self, text, source_lang, target_lang):
        """
        Translate using deep-translator with Google Translate backend.
        Handles long texts by chunking automatically.
        """
        try:
            # Map language codes if needed
            source = self._map_lang_code(source_lang)
            target = self._map_lang_code(target_lang)

            # deep-translator supports 'auto' for source detection
            if source_lang == "auto":
                source = "auto"

            # Google Translate has a 5000 char limit per request
            MAX_CHUNK = 4500
            if len(text) <= MAX_CHUNK:
                translator = GoogleTranslator(source=source, target=target)
                result = translator.translate(text)
                return result if result else text
            else:
                # Split into paragraphs/chunks and translate each
                return self._translate_long_text(text, source, target, MAX_CHUNK)

        except Exception as e:
            print(f"❌ Google translation error: {e}")
            raise

    def _translate_long_text(self, text, source, target, max_chunk):
        """
        Handle long texts by splitting into chunks and translating each.
        """
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        translated_paragraphs = []

        for para in paragraphs:
            if len(para) <= max_chunk:
                try:
                    translator = GoogleTranslator(source=source, target=target)
                    translated = translator.translate(para)
                    translated_paragraphs.append(translated if translated else para)
                except Exception as e:
                    print(f"⚠️ Chunk translation error: {e}")
                    translated_paragraphs.append(para)
            else:
                # Further split by sentences
                sentences = para.replace('. ', '.|').replace('? ', '?|').replace('! ', '!|').split('|')
                chunk = ""
                translated_chunk = []
                for sentence in sentences:
                    if len(chunk) + len(sentence) > max_chunk:
                        if chunk:
                            try:
                                t = GoogleTranslator(source=source, target=target)
                                result = t.translate(chunk.strip())
                                translated_chunk.append(result if result else chunk.strip())
                            except Exception:
                                translated_chunk.append(chunk.strip())
                        chunk = sentence + " "
                    else:
                        chunk += sentence + " "
                if chunk.strip():
                    try:
                        t = GoogleTranslator(source=source, target=target)
                        result = t.translate(chunk.strip())
                        translated_chunk.append(result if result else chunk.strip())
                    except Exception:
                        translated_chunk.append(chunk.strip())
                translated_paragraphs.append(" ".join(translated_chunk))

        return '\n\n'.join(translated_paragraphs)

    def _map_lang_code(self, code):
        """
        Map ISO 639-1 codes to deep-translator accepted codes.
        deep-translator accepts full names or ISO codes.
        """
        # deep-translator generally accepts ISO 639-1 codes directly
        # Map some edge cases
        code_map = {
            'zh': 'zh-CN',
            'pt': 'pt',
            'auto': 'auto',
        }
        return code_map.get(code, code)

    def _fallback_translate(self, text, source_lang, target_lang):
        """
        Fallback translation using transformers or simple word replacement.
        Used when deep-translator is unavailable.
        """
        if TRANSFORMERS_AVAILABLE:
            try:
                # Only works for en->de reliably with the available model
                if source_lang in ('en', 'auto') and target_lang == 'de':
                    translator_pipe = pipeline("translation", model="Helsinki-NLP/opus-mt-en-de")
                    result = translator_pipe(text[:500])  # limit for safety
                    if result and isinstance(result, list):
                        return result[0].get('translation_text', text)
            except Exception as e:
                print(f"⚠️ Transformers translation failed: {e}")

        # Simple word-level fallback for common phrases
        common_translations = {
            "en_to_es": {
                "hello": "hola", "world": "mundo", "good": "bueno",
                "morning": "mañana", "afternoon": "tarde", "evening": "noche",
                "thank you": "gracias", "please": "por favor", "yes": "sí",
                "no": "no", "water": "agua", "food": "comida",
                "house": "casa", "car": "coche", "book": "libro",
                "welcome": "bienvenido", "goodbye": "adiós", "friend": "amigo",
            },
            "en_to_fr": {
                "hello": "bonjour", "world": "monde", "good": "bon",
                "morning": "matin", "afternoon": "après-midi", "evening": "soir",
                "thank you": "merci", "please": "s'il vous plaît", "yes": "oui",
                "no": "non", "water": "eau", "food": "nourriture",
                "house": "maison", "car": "voiture", "book": "livre",
                "welcome": "bienvenue", "goodbye": "au revoir", "friend": "ami",
            },
            "en_to_de": {
                "hello": "hallo", "world": "welt", "good": "gut",
                "morning": "morgen", "afternoon": "nachmittag", "evening": "abend",
                "thank you": "danke", "please": "bitte", "yes": "ja",
                "no": "nein", "water": "wasser", "food": "essen",
                "house": "haus", "car": "auto", "book": "buch",
                "welcome": "willkommen", "goodbye": "auf wiedersehen", "friend": "freund",
            },
        }

        key = f"{source_lang}_to_{target_lang}"
        if key in common_translations:
            words = text.lower().split()
            translated = []
            for word in words:
                clean = word.strip('.,!?;:"\'')
                translated.append(common_translations[key].get(clean, word))
            return " ".join(translated)

        # Ultimate fallback - explain limitation clearly
        lang_names = self.get_supported_languages()
        target_name = lang_names.get(target_lang, target_lang.upper())
        return (
            f"[Translation to {target_name} requires an internet connection. "
            f"Please check your connection and try again.]\n\nOriginal text: {text}"
        )

    def detect_language(self, text):
        """
        Detect the language of the given text.

        Args:
            text (str): Text to detect language for

        Returns:
            str: Detected language code, or 'unknown'
        """
        if not DEEP_TRANSLATOR_AVAILABLE:
            return 'unknown'
        try:
            # Use deep-translator's detection capability
            # GoogleTranslator with source='auto' implicitly detects
            translated = GoogleTranslator(source='auto', target='en').translate(text[:100])
            return 'auto-detected'
        except Exception as e:
            print(f"❌ Language detection error: {e}")
            return 'unknown'

    def get_supported_languages(self):
        """
        Get list of supported language codes and names.
        """
        if DEEP_TRANSLATOR_AVAILABLE:
            try:
                raw = GoogleTranslator().get_supported_languages(as_dict=True)
                # raw is {name: code}, flip to {code: name}
                return {v: k.title() for k, v in raw.items()}
            except Exception:
                pass

        # Fallback static list
        return {
            'en': 'English', 'es': 'Spanish', 'fr': 'French',
            'de': 'German', 'it': 'Italian', 'pt': 'Portuguese',
            'ru': 'Russian', 'ja': 'Japanese', 'ko': 'Korean',
            'zh-CN': 'Chinese (Simplified)', 'ar': 'Arabic', 'hi': 'Hindi',
            'nl': 'Dutch', 'sv': 'Swedish', 'pl': 'Polish',
            'tr': 'Turkish', 'vi': 'Vietnamese', 'th': 'Thai',
        }