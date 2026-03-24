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

from flask import Flask, render_template, request, jsonify, send_file, send_from_directory, redirect, url_for, flash, session
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

# ---------------------------------------------------------------------------
# Auth Routes
# ---------------------------------------------------------------------------

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login page
    """
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember_me')

        # Demo authentication — replace with real DB lookup
        if email and password:
            # Accept any non-empty credentials for demo; swap with real check
            session['user_email'] = email
            session['logged_in'] = True
            flash('Welcome back! You are now signed in.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Please enter your email and password.', 'error')

    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    Sign-up / registration page
    """
    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not first_name or not email or not password or not confirm_password:
            flash('Please fill in all required fields.', 'error')
        elif password != confirm_password:
            flash('Passwords do not match. Please try again.', 'error')
        elif len(password) < 8:
            flash('Password must be at least 8 characters long.', 'error')
        else:
            # Account creation — replace with real DB save
            session['user_email'] = email
            session['user_name'] = first_name
            session['logged_in'] = True
            flash(f'Account created successfully! Welcome, {first_name}!', 'success')
            return redirect(url_for('index'))

    return render_template('signup.html')


@app.route('/logout')
def logout():
    """
    Log out the current user
    """
    session.clear()
    flash('You have been signed out.', 'success')
    return redirect(url_for('login'))


# ---------------------------------------------------------------------------
# Page Routes
# ---------------------------------------------------------------------------

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
    API endpoint for speech-to-text conversion.
    Accepts:
      - audio (file): the audio file
      - language (str): BCP-47 code for recognition, e.g. 'en-US' (default)
      - translate_to (str): ISO-639-1 code to translate the transcript into, e.g. 'hi'
    """
    temp_path = None
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'Audio file is required'}), 400

        audio_file = request.files['audio']

        if audio_file.filename == '':
            return jsonify({'error': 'No audio file selected'}), 400

        # Recognition language from form (BCP-47, e.g. 'hi-IN', 'en-US')
        language = request.form.get('language', 'en-US')

        # Optional translation target (ISO-639-1, e.g. 'hi', 'fr')
        translate_to = request.form.get('translate_to', '').strip()

        # Preserve original file extension so pydub can identify the format
        original_ext = os.path.splitext(audio_file.filename)[1] or '.wav'

        # Save uploaded file to a temporary path
        with tempfile.NamedTemporaryFile(delete=False, suffix=original_ext) as temp_file:
            temp_path = temp_file.name

        audio_file.save(temp_path)

        # Step 1: Transcribe in the chosen recognition language
        text = speech_to_text.convert_audio_to_text(temp_path, language=language)

        # Step 2: Translate if a different output language was requested
        translated_text = None
        if translate_to:
            # Derive a simple 2-letter base from BCP-47 (e.g. 'hi-IN' -> 'hi')
            recognition_base = language.split('-')[0].lower()
            target_base = translate_to.split('-')[0].lower()

            # Only translate if target differs from recognition language
            if recognition_base != target_base:
                try:
                    translated_text = translator.translate(
                        text, source_lang='auto', target_lang=target_base
                    )
                except Exception as te:
                    print(f"⚠️ Translation after transcription failed: {te}")

        return jsonify({
            'success': True,
            'text': translated_text if translated_text else text,
            'original_text': text if translated_text else None,
            'translated': bool(translated_text),
            'recognition_language': language,
            'output_language': translate_to or language,
        })

    except Exception as e:
        return jsonify({'error': f'Speech-to-text conversion failed: {str(e)}'}), 500
    finally:
        # Always clean up the temp file
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except Exception:
                pass

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

@app.route('/favicon.ico')
def favicon():
    """
    Serve favicon to prevent 404 errors in browser console
    """
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.svg',
        mimetype='image/svg+xml'
    )

@app.route('/api/detect-language', methods=['POST'])
def api_detect_language():
    """
    API endpoint for language detection
    """
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        detected = translator.detect_language(text)
        return jsonify({'success': True, 'language': detected})
    except Exception as e:
        return jsonify({'error': f'Language detection failed: {str(e)}'}), 500

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