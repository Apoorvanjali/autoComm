"""
Text-to-Speech Conversion Service
Uses gTTS (Google Text-to-Speech) for converting any text to natural audio.
"""

import os
import tempfile
import logging
from io import BytesIO

try:
    from gtts import gTTS, lang as gtts_lang
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    print("❌ gTTS not installed. Run: pip install gTTS")

# Supported language codes for gTTS
GTTS_SUPPORTED_LANGS = None  # lazy-loaded

# Known aliases: user-supplied code → exact gTTS code
# Keys are lowercase, values are the EXACT case gTTS expects
LANG_ALIASES = {
    'zh':    'zh-CN',
    'zh-cn': 'zh-CN',
    'zh-tw': 'zh-TW',
    'pt-br': 'pt',       # gTTS uses 'pt' for Brazilian Portuguese
    'pt-pt': 'pt',
    'en-us': 'en',
    'en-gb': 'en-uk',    # gTTS uses 'en-uk' for British English
    'en-au': 'en-au',
    'fr-ca': 'fr-CA',
    'es-mx': 'es',
    'es-es': 'es',
}


def _get_gtts_langs():
    """Lazily fetch and cache the gTTS supported language map."""
    global GTTS_SUPPORTED_LANGS
    if GTTS_SUPPORTED_LANGS is None and GTTS_AVAILABLE:
        try:
            # gTTS returns codes in their exact required case (e.g. 'zh-CN', 'en-uk')
            GTTS_SUPPORTED_LANGS = gtts_lang.tts_langs()
        except Exception:
            GTTS_SUPPORTED_LANGS = {}
    return GTTS_SUPPORTED_LANGS or {}


class TextToSpeechConverter:
    def __init__(self):
        if GTTS_AVAILABLE:
            print("✅ Text-to-Speech Converter initialized (Google TTS)")
        else:
            print("❌ gTTS not available - text-to-speech will not work")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def convert_text_to_speech(self, text, language='en', slow=False):
        """
        Convert text to an MP3 audio file.

        Args:
            text (str): Text to synthesize (any language, up to 5000 chars)
            language (str): BCP-47 or ISO 639-1 language code (e.g. 'hi', 'zh-CN', 'fr')
            slow (bool): If True, speak slowly

        Returns:
            str: Path to generated MP3 file
        """
        if not GTTS_AVAILABLE:
            raise RuntimeError("gTTS is not installed. Please run: pip install gTTS")

        text = text.strip()
        if not text:
            raise ValueError("Text cannot be empty.")

        MAX_CHARS = 5000
        if len(text) > MAX_CHARS:
            text = text[:MAX_CHARS]
            print(f"⚠️ Text truncated to {MAX_CHARS} characters for TTS")

        resolved = self._resolve_lang(language)
        print(f"🌐 Using language code: '{resolved}' (requested: '{language}')")

        try:
            tts = gTTS(text=text, lang=resolved, slow=slow)
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            temp_file.close()
            tts.save(temp_file.name)
            print(f"✅ Audio generated: {temp_file.name}")
            return temp_file.name

        except Exception as e:
            print(f"❌ gTTS error for lang='{resolved}': {e}")
            if resolved != 'en':
                print("⚠️ Retrying with English...")
                try:
                    tts = gTTS(text=text, lang='en', slow=slow)
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
                    temp_file.close()
                    tts.save(temp_file.name)
                    return temp_file.name
                except Exception as e2:
                    print(f"❌ English fallback also failed: {e2}")
            raise RuntimeError(f"Text-to-speech conversion failed: {str(e)}")

    def convert_text_to_speech_bytes(self, text, language='en', slow=False):
        """
        Convert text to speech and return raw MP3 bytes (for streaming).

        Returns:
            bytes: MP3 audio data, or None on failure
        """
        if not GTTS_AVAILABLE:
            return None

        try:
            text = text.strip()
            if not text:
                return None

            resolved = self._resolve_lang(language)
            print(f"🌐 Using language code: '{resolved}' (requested: '{language}')")

            tts = gTTS(text=text[:5000], lang=resolved, slow=slow)
            buf = BytesIO()
            tts.write_to_fp(buf)
            buf.seek(0)
            return buf.read()

        except Exception as e:
            print(f"❌ TTS bytes conversion error: {e}")
            return None

    def play_audio(self, audio_file_path):
        """
        Audio playback is handled by the browser in a web app context.
        Kept for API compatibility.
        """
        print("ℹ️ Server-side audio playback is not used in web mode.")
        return False

    def cleanup_temp_files(self, file_path):
        """Delete a temporary audio file."""
        try:
            if file_path and os.path.exists(file_path):
                os.unlink(file_path)
                print(f"🗑️ Cleaned up: {file_path}")
        except Exception as e:
            print(f"⚠️ Could not delete {file_path}: {e}")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _resolve_lang(self, language):
        """
        Resolve a user-supplied language code to the exact code gTTS expects.

        Resolution order:
          1. Check LANG_ALIASES (handles zh-CN, zh-TW, pt-BR, en-GB, etc.)
          2. Exact match in gTTS supported langs (case-insensitive search)
          3. Base-language match (strip region, e.g. 'fr-FR' → 'fr')
          4. Fall back to 'en'
        """
        if not language:
            return 'en'

        lang_lower = language.lower().strip()

        # --- Step 1: check our alias table first ---
        if lang_lower in LANG_ALIASES:
            alias = LANG_ALIASES[lang_lower]
            # Verify alias is actually supported before using it
            supported = _get_gtts_langs()
            if not supported or alias in supported:
                return alias

        # --- Step 2: exact match (case-insensitive) against gTTS list ---
        supported = _get_gtts_langs()
        if supported:
            # Build a lowercase→original map once per call (cheap)
            lower_map = {k.lower(): k for k in supported}

            if lang_lower in lower_map:
                return lower_map[lang_lower]  # return the EXACT case gTTS wants

            # --- Step 3: try base language (e.g. 'de-AT' → 'de') ---
            base = lang_lower.split('-')[0]
            if base in lower_map:
                return lower_map[base]

            print(f"⚠️ Language '{language}' not supported by gTTS, falling back to English")
            return 'en'

        # --- Step 4: gTTS lang list unavailable, trust the caller ---
        # Return the original (not lowercased) so case-sensitive codes like zh-CN work
        return language.strip()

    def get_supported_languages(self):
        """Return supported language codes with display names."""
        supported = _get_gtts_langs()
        if supported:
            return {code: name.title() for code, name in supported.items()}

        # Static fallback
        return {
            'en':    'English',      'es':    'Spanish',     'fr':    'French',
            'de':    'German',       'it':    'Italian',     'pt':    'Portuguese',
            'ru':    'Russian',      'ja':    'Japanese',    'ko':    'Korean',
            'zh-CN': 'Chinese (Simplified)', 'zh-TW': 'Chinese (Traditional)',
            'ar':    'Arabic',       'hi':    'Hindi',       'nl':    'Dutch',
            'sv':    'Swedish',      'da':    'Danish',      'no':    'Norwegian',
            'fi':    'Finnish',      'pl':    'Polish',      'tr':    'Turkish',
            'uk':    'Ukrainian',    'cs':    'Czech',       'bn':    'Bengali',
            'ta':    'Tamil',        'te':    'Telugu',      'ml':    'Malayalam',
            'gu':    'Gujarati',     'mr':    'Marathi',     'pa':    'Punjabi',
        }