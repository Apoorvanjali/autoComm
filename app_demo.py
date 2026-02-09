"""
AutoComm - AI-Powered Communication and Content Automation Suite
Main Flask Application - Demo Version with Fallback AI Services

This version works without requiring PyTorch or heavy AI dependencies
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
import tempfile

# Import simple fallback services
from services.email_service import EmailService

# Initialize Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'autocomm-secret-key-2024'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize services
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

# API Routes for AI Services (Demo Versions)

@app.route('/api/summarize', methods=['POST'])
def api_summarize():
    """
    API endpoint for text summarization (Demo version)
    """
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        if len(text) < 100:
            return jsonify({'error': 'Text must be at least 100 characters long for meaningful summarization'}), 400
        
        # Demo summarization using simple extraction
        summary = create_demo_summary(text)
        
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
    API endpoint for language translation (Demo version)
    """
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        source_lang = data.get('source_language', 'auto')
        target_lang = data.get('target_language', 'en')
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        # Demo translation
        translation = create_demo_translation(text, source_lang, target_lang)
        
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
    API endpoint for speech-to-text conversion (Demo version)
    """
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'Audio file is required'}), 400
        
        audio_file = request.files['audio']
        
        if audio_file.filename == '':
            return jsonify({'error': 'No audio file selected'}), 400
        
        # Demo speech-to-text
        text = f"Demo transcription: This is a sample transcription of the uploaded audio file '{audio_file.filename}'. In a full version, this would contain the actual speech-to-text conversion using Google Speech API or similar services."
        
        return jsonify({
            'success': True,
            'text': text
        })
        
    except Exception as e:
        return jsonify({'error': f'Speech-to-text conversion failed: {str(e)}'}), 500

@app.route('/api/text-to-speech', methods=['POST'])
def api_text_to_speech():
    """
    API endpoint for text-to-speech conversion (Demo version)
    """
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        language = data.get('language', 'en')
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        # Create a demo text file instead of audio (since gTTS requires internet)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.txt', mode='w')
        temp_file.write(f"Text-to-Speech Demo Output:\n\n{text}\n\nLanguage: {language}\n\nIn the full version, this would be an MP3 audio file generated using Google Text-to-Speech API.")
        temp_file.close()
        
        return send_file(
            temp_file.name,
            as_attachment=True,
            download_name='speech_demo.txt',
            mimetype='text/plain'
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

def create_demo_summary(text):
    """
    Create a demo summary using simple text extraction
    """
    sentences = text.split('. ')
    if len(sentences) <= 3:
        return text
    
    # Take first sentence, a middle sentence, and last sentence
    summary_sentences = []
    
    # First sentence
    summary_sentences.append(sentences[0])
    
    # Middle sentence
    middle_idx = len(sentences) // 2
    if middle_idx < len(sentences) - 1:
        summary_sentences.append(sentences[middle_idx])
    
    # Last sentence
    if len(sentences) > 1:
        summary_sentences.append(sentences[-1])
    
    summary = '. '.join(summary_sentences)
    if not summary.endswith('.'):
        summary += '.'
    
    return f"[DEMO SUMMARY] {summary}\n\nNote: This is a demonstration summary created using simple text extraction. The full version uses AI models like BART for intelligent summarization."

def create_demo_translation(text, source_lang, target_lang):
    """
    Create a demo translation
    """
    # Simple word replacements for demo
    demo_translations = {
        'hello': {'es': 'hola', 'fr': 'bonjour', 'de': 'hallo', 'it': 'ciao'},
        'world': {'es': 'mundo', 'fr': 'monde', 'de': 'welt', 'it': 'mondo'},
        'good': {'es': 'bueno', 'fr': 'bon', 'de': 'gut', 'it': 'buono'},
        'morning': {'es': 'mañana', 'fr': 'matin', 'de': 'morgen', 'it': 'mattina'},
        'thank you': {'es': 'gracias', 'fr': 'merci', 'de': 'danke', 'it': 'grazie'}
    }
    
    words = text.lower().split()
    translated_words = []
    
    for word in words:
        clean_word = word.strip('.,!?;:"')
        if clean_word in demo_translations and target_lang in demo_translations[clean_word]:
            translated_words.append(demo_translations[clean_word][target_lang])
        else:
            translated_words.append(word)
    
    translated_text = ' '.join(translated_words)
    
    return f"[DEMO TRANSLATION] {translated_text}\n\nNote: This is a demonstration translation with basic word replacements. The full version uses AI models like Helsinki-NLP for accurate translation."

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
    print("🤖 Running in DEMO mode with fallback AI services")
    print("💡 Install PyTorch and other AI dependencies for full functionality")
    
    # Run the Flask application
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000,
        threaded=True
    )