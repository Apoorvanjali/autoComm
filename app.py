"""
AutoComm - AI-Powered Communication and Content Automation Suite
Main Flask Application

This application provides AI-powered text processing features including:
- Text Summarization
- Language Translation
- Speech-to-Text conversion
- Text-to-Speech conversion
- Intelligent Email Automation
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
import tempfile
from services.summarizer import TextSummarizer
from services.translator import LanguageTranslator
from services.speech_to_text import SpeechToTextConverter
from services.text_to_speech import TextToSpeechConverter
from services.email_service import EmailService

# Initialize Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'autocomm-secret-key-2024'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize AI services
summarizer = TextSummarizer()
translator = LanguageTranslator()
speech_to_text = SpeechToTextConverter()
text_to_speech = TextToSpeechConverter()
email_service = EmailService()

@app.route('/')
def index():
    """
    Home page route - displays the main dashboard
    """
    return render_template('index.html')

@app.route('/summarizer')
def summarizer_page():
    """
    Text Summarization page
    """
    return render_template('summarizer.html')

@app.route('/translator')
def translator_page():
    """
    Language Translation page
    """
    return render_template('translator.html')

@app.route('/speech')
def speech_page():
    """
    Speech processing page (Speech-to-Text and Text-to-Speech)
    """
    return render_template('speech.html')

@app.route('/email')
def email_page():
    """
    Email automation page
    """
    return render_template('email.html')

# API Routes for AI Services

@app.route('/api/summarize', methods=['POST'])
def api_summarize():
    """
    API endpoint for text summarization
    """
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        summary_length = data.get('summary_length', 'medium')
        summary_style = data.get('summary_style', 'paragraph')
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        if len(text) < 100:
            return jsonify({'error': 'Text must be at least 100 characters long for meaningful summarization'}), 400
        
        # Generate summary using AI service with length and style options
        summary = summarizer.summarize(text, length=summary_length, style=summary_style)
        
        return jsonify({
            'success': True,
            'summary': summary,
            'original_length': len(text),
            'summary_length': len(summary)
        })
        
    except Exception as e:
        return jsonify({'error': f'Summarization failed: {str(e)}'}), 500

@app.route('/api/translate', methods=['POST'])
def api_translate():
    """
    API endpoint for language translation
    """
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        source_lang = data.get('source_language', 'auto')
        target_lang = data.get('target_language', 'en')
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        # Translate text using AI service
        translation = translator.translate(text, source_lang, target_lang)
        
        return jsonify({
            'success': True,
            'translation': translation,
            'source_language': source_lang,
            'target_language': target_lang
        })
        
    except Exception as e:
        return jsonify({'error': f'Translation failed: {str(e)}'}), 500

@app.route('/api/speech-to-text', methods=['POST'])
def api_speech_to_text():
    """
    API endpoint for speech-to-text conversion
    """
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'Audio file is required'}), 400
        
        audio_file = request.files['audio']
        
        if audio_file.filename == '':
            return jsonify({'error': 'No audio file selected'}), 400
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            audio_file.save(temp_file.name)
            
            # Convert speech to text
            text = speech_to_text.convert_audio_to_text(temp_file.name)
            
            # Clean up temporary file
            os.unlink(temp_file.name)
            
            return jsonify({
                'success': True,
                'text': text
            })
            
    except Exception as e:
        return jsonify({'error': f'Speech-to-text conversion failed: {str(e)}'}), 500

@app.route('/api/text-to-speech', methods=['POST'])
def api_text_to_speech():
    """
    API endpoint for text-to-speech conversion
    """
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        language = data.get('language', 'en')
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        # Convert text to speech
        audio_file_path = text_to_speech.convert_text_to_speech(text, language)
        
        # Return the audio file
        return send_file(
            audio_file_path,
            as_attachment=True,
            download_name='speech.mp3',
            mimetype='audio/mpeg'
        )
        
    except Exception as e:
        return jsonify({'error': f'Text-to-speech conversion failed: {str(e)}'}), 500

@app.route('/api/send-email', methods=['POST'])
def api_send_email():
    """
    API endpoint for automated email sending
    """
    try:
        data = request.get_json()
        sender_email = data.get('sender_email', '').strip()
        sender_password = data.get('sender_password', '').strip()
        receiver_email = data.get('receiver_email', '').strip()
        subject = data.get('subject', '').strip()
        message = data.get('message', '').strip()
        
        # Validate required fields
        if not all([sender_email, sender_password, receiver_email, subject, message]):
            return jsonify({'error': 'All fields are required'}), 400
        
        # Send email using email service
        success = email_service.send_email(
            sender_email, 
            sender_password, 
            receiver_email, 
            subject, 
            message
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Email sent successfully!'
            })
        else:
            return jsonify({'error': 'Failed to send email. Please check your credentials and try again.'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Email sending failed: {str(e)}'}), 500

@app.errorhandler(404)
def not_found(error):
    """
    Handle 404 errors
    """
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """
    Handle 500 errors
    """
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Create necessary directories if they don't exist
    os.makedirs('static/uploads', exist_ok=True)
    os.makedirs('static/temp', exist_ok=True)
    
    print("🚀 AutoComm - AI-Powered Communication Suite Starting...")
    print("📍 Access the application at: http://localhost:5000")
    print("🤖 AI Services: Summarization, Translation, Speech Processing, Email Automation")
    
    # Run the Flask application
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000,
        threaded=True
    )