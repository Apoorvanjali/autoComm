"""
Speech-to-Text Conversion Service
Uses speech_recognition library for converting audio to text
"""

import speech_recognition as sr
import os
import tempfile
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    print("⚠️ PyDub not available, audio conversion limited")

import logging

class SpeechToTextConverter:
    def __init__(self):
        """
        Initialize the speech recognition engine
        """
        try:
            # Initialize the recognizer
            self.recognizer = sr.Recognizer()
            
            # Adjust for ambient noise (helps with accuracy)
            self.recognizer.energy_threshold = 300
            self.recognizer.dynamic_energy_threshold = True
            
            print("✅ Speech-to-Text Converter initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize speech-to-text converter: {e}")

    def convert_audio_to_text(self, audio_file_path, language='en-US'):
        """
        Convert audio file to text using speech recognition
        
        Args:
            audio_file_path (str): Path to the audio file
            language (str): Language code for recognition
            
        Returns:
            str: Transcribed text from audio
        """
        try:
            # Convert audio to WAV format if needed
            wav_path = self._ensure_wav_format(audio_file_path)
            
            # Load and process the audio file
            with sr.AudioFile(wav_path) as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Record the audio data
                audio_data = self.recognizer.record(source)
            
            # Try multiple recognition methods
            text = self._recognize_with_fallback(audio_data, language)
            
            # Clean up temporary file if created
            if wav_path != audio_file_path:
                try:
                    os.unlink(wav_path)
                except:
                    pass
            
            return text if text else "Could not understand the audio. Please try with clearer speech."
            
        except Exception as e:
            print(f"❌ Speech-to-text conversion error: {e}")
            return f"Error processing audio: {str(e)}"

    def _ensure_wav_format(self, audio_file_path):
        """
        Convert audio file to WAV format if it's not already
        """
        if not PYDUB_AVAILABLE:
            # Return original file if pydub is not available
            print("⚠️ Audio conversion not available, using original file")
            return audio_file_path
            
        try:
            # Check if file is already WAV
            if audio_file_path.lower().endswith('.wav'):
                return audio_file_path
            
            # Convert to WAV
            audio = AudioSegment.from_file(audio_file_path)
            
            # Create temporary WAV file
            temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            temp_wav.close()
            
            # Export as WAV
            audio.export(temp_wav.name, format="wav")
            
            return temp_wav.name
            
        except Exception as e:
            print(f"⚠️  Audio conversion warning: {e}")
            # Return original file if conversion fails
            return audio_file_path

    def _recognize_with_fallback(self, audio_data, language):
        """
        Try multiple recognition engines with fallback
        """
        recognition_methods = [
            ('Google', self._recognize_google),
            ('Sphinx', self._recognize_sphinx),
            ('Fallback', self._recognize_fallback)
        ]
        
        for method_name, method_func in recognition_methods:
            try:
                print(f"🔍 Trying {method_name} recognition...")
                result = method_func(audio_data, language)
                if result and result.strip():
                    print(f"✅ {method_name} recognition successful")
                    return result.strip()
            except Exception as e:
                print(f"⚠️  {method_name} recognition failed: {e}")
                continue
        
        return None

    def _recognize_google(self, audio_data, language):
        """
        Use Google Speech Recognition (requires internet)
        """
        try:
            return self.recognizer.recognize_google(audio_data, language=language)
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            print(f"Google Speech Recognition service error: {e}")
            return None

    def _recognize_sphinx(self, audio_data, language):
        """
        Use CMU Sphinx (offline recognition)
        """
        try:
            return self.recognizer.recognize_sphinx(audio_data)
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            print(f"Sphinx recognition error: {e}")
            return None

    def _recognize_fallback(self, audio_data, language):
        """
        Fallback method - return a placeholder message
        """
        return "Audio processed - automatic transcription not available. Please try with a different audio file or check your internet connection."

    def convert_microphone_to_text(self, language='en-US', timeout=10):
        """
        Convert microphone input to text (for future implementation)
        
        Args:
            language (str): Language code for recognition
            timeout (int): Timeout in seconds
            
        Returns:
            str: Transcribed text from microphone
        """
        try:
            # Check if microphone is available
            mic_list = sr.Microphone.list_microphone_names()
            if not mic_list:
                return "No microphone detected on this system"
            
            with sr.Microphone() as source:
                print("🎤 Adjusting for ambient noise... Please wait.")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                print(f"🎤 Listening for {timeout} seconds... Speak now!")
                audio_data = self.recognizer.listen(source, timeout=timeout)
                
                print("🔍 Processing speech...")
                text = self._recognize_with_fallback(audio_data, language)
                
                return text if text else "Could not understand the speech. Please try again."
                
        except Exception as e:
            print(f"❌ Microphone recognition error: {e}")
            return f"Microphone error: {str(e)}"

    def get_supported_languages(self):
        """
        Get supported language codes for speech recognition
        """
        return {
            'en-US': 'English (US)',
            'en-GB': 'English (UK)',
            'es-ES': 'Spanish (Spain)',
            'es-MX': 'Spanish (Mexico)',
            'fr-FR': 'French',
            'de-DE': 'German',
            'it-IT': 'Italian',
            'pt-BR': 'Portuguese (Brazil)',
            'ru-RU': 'Russian',
            'ja-JP': 'Japanese',
            'ko-KR': 'Korean',
            'zh-CN': 'Chinese (Mandarin)',
            'ar-SA': 'Arabic',
            'hi-IN': 'Hindi'
        }