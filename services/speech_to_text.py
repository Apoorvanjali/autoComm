"""
Speech-to-Text Conversion Service
Uses Google Web Speech API via SpeechRecognition library.
Handles any audio file format robustly.
"""

import os
import tempfile
import logging

try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False
    print("❌ SpeechRecognition library not installed. Run: pip install SpeechRecognition")

try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    print("⚠️ PyDub not available — only WAV files accepted for speech recognition")


class SpeechToTextConverter:
    def __init__(self):
        """
        Initialize the speech recognition engine.
        """
        if not SR_AVAILABLE:
            print("❌ SpeechRecognition not available")
            self.recognizer = None
            return

        try:
            self.recognizer = sr.Recognizer()
            # Tuned thresholds for better accuracy
            self.recognizer.energy_threshold = 300
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.8
            print("✅ Speech-to-Text Converter initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize speech-to-text: {e}")
            self.recognizer = None

    def convert_audio_to_text(self, audio_file_path, language='en-US'):
        """
        Convert an audio file to text.

        Args:
            audio_file_path (str): Path to audio file (WAV, MP3, OGG, FLAC, etc.)
            language (str): BCP-47 language code, e.g. 'en-US', 'es-ES'

        Returns:
            str: Transcribed text or descriptive error message
        """
        if not SR_AVAILABLE or self.recognizer is None:
            return "Speech recognition library is not available. Please install: pip install SpeechRecognition"

        if not os.path.exists(audio_file_path):
            return "Audio file not found. Please upload a valid audio file."

        if os.path.getsize(audio_file_path) == 0:
            return "The uploaded audio file is empty. Please upload a file with actual audio content."

        wav_path = None
        try:
            # Convert to WAV if necessary
            wav_path = self._to_wav(audio_file_path)
            if wav_path is None:
                return "Could not process audio file. Please upload a WAV, MP3, OGG, or FLAC file."

            # Load and recognize
            with sr.AudioFile(wav_path) as source:
                # Adjust for noise in the first 0.5 seconds
                try:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                except Exception:
                    pass  # Continue even if noise adjustment fails
                audio_data = self.recognizer.record(source)

            text = self._recognize_with_fallback(audio_data, language)
            return text or "Could not understand the audio. Please ensure the recording has clear speech."

        except sr.UnknownValueError:
            return "No speech detected in the audio. Please upload a file with clear spoken words."
        except sr.RequestError as e:
            return (
                f"Speech recognition service error: {str(e)}. "
                "Please check your internet connection and try again."
            )
        except Exception as e:
            print(f"❌ Speech-to-text error: {e}")
            return f"Error processing audio file: {str(e)}. Please try again with a different file."
        finally:
            # Clean up temp WAV if it was created
            if wav_path and wav_path != audio_file_path and os.path.exists(wav_path):
                try:
                    os.unlink(wav_path)
                except Exception:
                    pass

    def _to_wav(self, audio_file_path):
        """
        Convert any audio file to WAV format for speech recognition.
        Falls back to original if conversion not possible.
        """
        file_lower = audio_file_path.lower()

        # Already WAV — check if it's a valid WAV
        if file_lower.endswith('.wav'):
            return audio_file_path

        if not PYDUB_AVAILABLE:
            print("⚠️ PyDub not available, attempting to use file as-is")
            # Try the file as-is in case it is actually PCM/WAV
            return audio_file_path

        try:
            # Determine format from extension
            ext = os.path.splitext(file_lower)[1].lstrip('.')
            format_map = {
                'mp3': 'mp3', 'ogg': 'ogg', 'flac': 'flac',
                'aac': 'aac', 'm4a': 'mp4', 'webm': 'webm',
                'wma': 'asf', 'aiff': 'aiff', 'opus': 'opus',
            }
            fmt = format_map.get(ext, ext) or 'mp3'

            audio = AudioSegment.from_file(audio_file_path, format=fmt)

            # Convert to mono, 16kHz — optimal for speech recognition
            audio = audio.set_channels(1).set_frame_rate(16000)

            temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            temp_wav.close()
            audio.export(temp_wav.name, format='wav')
            print(f"✅ Audio converted to WAV: {temp_wav.name}")
            return temp_wav.name

        except Exception as e:
            print(f"⚠️ Audio conversion failed: {e} — trying original file")
            return audio_file_path

    def _recognize_with_fallback(self, audio_data, language):
        """
        Try Google Speech Recognition first, then offline fallback.
        """
        # 1. Google Web Speech API (best quality, requires internet)
        try:
            text = self.recognizer.recognize_google(audio_data, language=language)
            if text and text.strip():
                print(f"✅ Google recognition succeeded")
                return text.strip()
        except sr.UnknownValueError:
            print("⚠️ Google: could not understand audio")
        except sr.RequestError as e:
            print(f"⚠️ Google request error: {e}")
        except Exception as e:
            print(f"⚠️ Google recognition error: {e}")

        # 2. CMU Sphinx (offline — may not be installed)
        try:
            text = self.recognizer.recognize_sphinx(audio_data)
            if text and text.strip():
                print("✅ Sphinx recognition succeeded (offline)")
                return text.strip()
        except Exception as e:
            print(f"⚠️ Sphinx recognition unavailable: {e}")

        return None

    def convert_microphone_to_text(self, language='en-US', timeout=10):
        """
        Record from microphone and transcribe.
        """
        if not SR_AVAILABLE or self.recognizer is None:
            return "Speech recognition library is not available."

        try:
            mic_list = sr.Microphone.list_microphone_names()
            if not mic_list:
                return "No microphone found on this system."

            with sr.Microphone() as source:
                print("🎤 Adjusting for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print(f"🎤 Listening (timeout: {timeout}s)...")
                audio_data = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=30)

            text = self._recognize_with_fallback(audio_data, language)
            return text or "Could not understand the speech. Please speak more clearly and try again."

        except sr.WaitTimeoutError:
            return "No speech detected within the timeout period. Please try again and speak sooner."
        except Exception as e:
            print(f"❌ Microphone recognition error: {e}")
            return f"Microphone error: {str(e)}"

    def get_supported_languages(self):
        """
        Supported BCP-47 language codes for Google Speech Recognition.
        """
        return {
            'en-US': 'English (US)', 'en-GB': 'English (UK)',
            'es-ES': 'Spanish (Spain)', 'es-MX': 'Spanish (Mexico)',
            'fr-FR': 'French', 'de-DE': 'German',
            'it-IT': 'Italian', 'pt-BR': 'Portuguese (Brazil)',
            'ru-RU': 'Russian', 'ja-JP': 'Japanese',
            'ko-KR': 'Korean', 'zh-CN': 'Chinese (Mandarin)',
            'ar-SA': 'Arabic', 'hi-IN': 'Hindi',
            'nl-NL': 'Dutch', 'pl-PL': 'Polish',
            'sv-SE': 'Swedish', 'da-DK': 'Danish',
        }