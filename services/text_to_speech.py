"""
Text-to-Speech Conversion Service
Uses gTTS (Google Text-to-Speech) for converting text to audio
"""

from gtts import gTTS
import os
import tempfile
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("⚠️ Pygame not available, audio playback limited")

from io import BytesIO
import logging

class TextToSpeechConverter:
    def __init__(self):
        """
        Initialize the text-to-speech converter
        """
        if PYGAME_AVAILABLE:
            try:
                # Initialize pygame mixer for audio playback (optional)
                pygame.mixer.init()
                print("✅ Text-to-Speech Converter initialized successfully")
            except Exception as e:
                print(f"⚠️  Text-to-Speech initialized with limited functionality: {e}")
        else:
            print("✅ Text-to-Speech Converter initialized (no audio playback)")

    def convert_text_to_speech(self, text, language='en', slow=False):
        """
        Convert text to speech and return audio file path
        
        Args:
            text (str): Text to convert to speech
            language (str): Language code for speech
            slow (bool): Whether to speak slowly
            
        Returns:
            str: Path to generated audio file
        """
        try:
            # Clean and validate input text
            text = text.strip()
            if not text:
                raise ValueError("Text cannot be empty")
            
            if len(text) > 5000:  # Limit text length
                text = text[:5000] + "..."
                print("⚠️  Text truncated to 5000 characters")
            
            # Create gTTS object
            tts = gTTS(text=text, lang=language, slow=slow)
            
            # Create temporary file for audio
            temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            temp_audio.close()
            
            # Save audio to temporary file
            tts.save(temp_audio.name)
            
            print(f"✅ Audio generated successfully: {temp_audio.name}")
            return temp_audio.name
            
        except Exception as e:
            print(f"❌ Text-to-speech conversion error: {e}")
            return self._create_fallback_audio(text, language)

    def _create_fallback_audio(self, text, language):
        """
        Create a fallback audio file when gTTS fails
        """
        try:
            # Create a simple text file as fallback
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.txt', mode='w')
            temp_file.write(f"Text-to-Speech Output:\n\n{text}\n\nLanguage: {language}")
            temp_file.close()
            
            print(f"⚠️  Fallback: Created text file instead of audio: {temp_file.name}")
            return temp_file.name
            
        except Exception as e:
            print(f"❌ Fallback creation failed: {e}")
            return None

    def play_audio(self, audio_file_path):
        """
        Play the generated audio file
        
        Args:
            audio_file_path (str): Path to audio file
        """
        if not PYGAME_AVAILABLE:
            print("⚠️ Audio playback not available (pygame not installed)")
            return False
            
        try:
            if not os.path.exists(audio_file_path):
                print("❌ Audio file not found")
                return False
            
            # Try to play using pygame
            pygame.mixer.music.load(audio_file_path)
            pygame.mixer.music.play()
            
            print("🔊 Playing audio...")
            
            # Wait for playback to complete
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)
            
            return True
            
        except Exception as e:
            print(f"❌ Audio playback error: {e}")
            return False

    def convert_text_to_speech_bytes(self, text, language='en', slow=False):
        """
        Convert text to speech and return as bytes (for web streaming)
        
        Args:
            text (str): Text to convert
            language (str): Language code
            slow (bool): Whether to speak slowly
            
        Returns:
            bytes: Audio data as bytes
        """
        try:
            text = text.strip()
            if not text:
                return None
            
            # Create gTTS object
            tts = gTTS(text=text, lang=language, slow=slow)
            
            # Save to BytesIO buffer
            audio_buffer = BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            
            return audio_buffer.read()
            
        except Exception as e:
            print(f"❌ Text-to-speech bytes conversion error: {e}")
            return None

    def get_supported_languages(self):
        """
        Get supported language codes for text-to-speech
        """
        return {
            'en': 'English',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'ja': 'Japanese',
            'ko': 'Korean',
            'zh': 'Chinese (Mandarin)',
            'ar': 'Arabic',
            'hi': 'Hindi',
            'nl': 'Dutch',
            'sv': 'Swedish',
            'da': 'Danish',
            'no': 'Norwegian',
            'fi': 'Finnish',
            'pl': 'Polish',
            'cs': 'Czech',
            'sk': 'Slovak',
            'hu': 'Hungarian',
            'ro': 'Romanian',
            'bg': 'Bulgarian',
            'hr': 'Croatian',
            'sl': 'Slovenian',
            'et': 'Estonian',
            'lv': 'Latvian',
            'lt': 'Lithuanian'
        }

    def cleanup_temp_files(self, file_path):
        """
        Clean up temporary audio files
        
        Args:
            file_path (str): Path to file to delete
        """
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
                print(f"🗑️  Cleaned up temporary file: {file_path}")
        except Exception as e:
            print(f"⚠️  Could not clean up file {file_path}: {e}")

    def batch_convert(self, texts, language='en', output_dir=None):
        """
        Convert multiple texts to speech files
        
        Args:
            texts (list): List of texts to convert
            language (str): Language code
            output_dir (str): Directory to save files
            
        Returns:
            list: List of generated file paths
        """
        try:
            if not output_dir:
                output_dir = tempfile.mkdtemp()
            
            audio_files = []
            
            for i, text in enumerate(texts):
                if not text.strip():
                    continue
                
                try:
                    tts = gTTS(text=text.strip(), lang=language)
                    
                    file_path = os.path.join(output_dir, f"speech_{i+1}.mp3")
                    tts.save(file_path)
                    audio_files.append(file_path)
                    
                    print(f"✅ Generated audio {i+1}/{len(texts)}")
                    
                except Exception as e:
                    print(f"⚠️  Failed to generate audio for text {i+1}: {e}")
                    continue
            
            return audio_files
            
        except Exception as e:
            print(f"❌ Batch conversion error: {e}")
            return []