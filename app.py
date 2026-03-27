"""
AutoComm - AI-Powered Communication and Content Automation Suite
Main Flask Application

This application provides AI-powered text processing features including:
- Text Summarization
- Language Translation
- Speech-to-Text conversion
- Text-to-Speech conversion
- Intelligent Email Automation
- Plagiarism Detection
"""

from flask import Flask, render_template, request, jsonify, send_file, send_from_directory, redirect, url_for, flash, session
import os
import tempfile
import uuid
from services.summarizer import TextSummarizer
from services.translator import LanguageTranslator
from services.speech_to_text import SpeechToTextConverter
from services.text_to_speech import TextToSpeechConverter
from services.email_service import EmailService
from services.plagiarism_checker import PlagiarismChecker
from services.workflow_automation import WorkflowAutomationService
from services.history_service import HistoryService

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
plagiarism_checker = PlagiarismChecker()
workflow_automation = WorkflowAutomationService(
    summarizer=summarizer,
    translator=translator,
    text_to_speech=text_to_speech,
    email_service=email_service,
    plagiarism_checker=plagiarism_checker,
)
history_service = HistoryService()

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
    supported_tts_languages = text_to_speech.get_supported_languages()
    tts_language_options = sorted(supported_tts_languages.items(), key=lambda x: x[1])
    return render_template('speech.html', tts_language_options=tts_language_options)

@app.route('/email')
def email_page():
    """
    Email automation page
    """
    return render_template('email.html')

@app.route('/plagiarism')
def plagiarism_page():
    """
    Plagiarism detection and content verification page
    """
    return render_template('plagiarism.html')

@app.route('/automation')
def automation_page():
    """
    End-to-end automation page
    """
    supported_languages = translator.get_supported_languages()
    # Normalize to a stable list of (code, name) for template rendering
    language_options = sorted(supported_languages.items(), key=lambda x: x[1])
    return render_template('automation.html', language_options=language_options)


@app.route('/workflow-composer')
def workflow_composer_page():
    """
    Custom workflow composer page
    """
    translate_languages = sorted(translator.get_supported_languages().items(), key=lambda x: x[1])
    tts_languages = sorted(text_to_speech.get_supported_languages().items(), key=lambda x: x[1])
    return render_template(
        'workflow_composer.html',
        translate_languages=translate_languages,
        tts_languages=tts_languages,
    )


@app.route('/history')
def history_page():
    """
    User history and favorites page
    """
    return render_template('history.html')

# API Routes for AI Services

@app.route('/api/summarize', methods=['POST'])
def api_summarize():
    """
    API endpoint for text or file summarization.
    Supports:
      - JSON body with text
      - multipart/form-data with file (.pdf, .docx, .pptx, .txt, .text, .md)
    """
    temp_path = None
    try:
        text = ''
        summary_length = 'medium'
        summary_style = 'paragraph'
        input_source = 'text'
        uploaded_name = None

        # File mode (multipart upload)
        if 'file' in request.files and request.files['file'].filename:
            uploaded = request.files['file']
            uploaded_name = uploaded.filename
            summary_length = request.form.get('summary_length', 'medium')
            summary_style = request.form.get('summary_style', 'paragraph')
            input_source = 'file'

            allowed_extensions = {'.pdf', '.docx', '.pptx', '.txt', '.text', '.md'}
            file_ext = os.path.splitext(uploaded.filename)[1].lower()
            if file_ext not in allowed_extensions:
                return jsonify({'error': 'Unsupported file format. Allowed: PDF, DOCX, PPTX, TXT, MD'}), 400

            with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
                temp_path = temp_file.name

            uploaded.save(temp_path)
            text = (plagiarism_checker.extract_text_from_file(temp_path) or '').strip()
        else:
            # Text mode (JSON or form)
            data = request.get_json(silent=True) if request.is_json else request.form
            text = (data.get('text', '') if data else '').strip()
            summary_length = (data.get('summary_length', 'medium') if data else 'medium')
            summary_style = (data.get('summary_style', 'paragraph') if data else 'paragraph')

        if not text:
            return jsonify({'error': 'No readable text found. Provide text input or upload a supported file.'}), 400
        
        if len(text) < 100:
            return jsonify({'error': 'Text must be at least 100 characters long for meaningful summarization'}), 400
        
        # Generate summary using AI service with length and style options
        summary = summarizer.summarize(text, length=summary_length, style=summary_style)
        
        return jsonify({
            'success': True,
            'summary': summary,
            'original_length': len(text),
            'summary_length': len(summary),
            'input_source': input_source,
            'file_name': uploaded_name,
        })
        
    except Exception as e:
        return jsonify({'error': f'Summarization failed: {str(e)}'}), 500
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except Exception:
                pass


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
            recognition_base = language.split('-')[0].lower()
            target_base = translate_to.split('-')[0].lower()

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

    except (ValueError, FileNotFoundError) as e:
        return jsonify({'error': str(e)}), 400
    except RuntimeError as e:
        return jsonify({'error': str(e)}), 503
    except Exception as e:
        return jsonify({'error': f'Speech-to-text conversion failed: {str(e)}'}), 500
    finally:
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

@app.route('/api/check-plagiarism-text', methods=['POST'])
def api_check_plagiarism_text():
    """
    API endpoint for plagiarism detection from plain text
    """
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        check_mode = data.get('check_mode', 'advanced')
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        if len(text.split()) < 10:
            return jsonify({
                'error': 'Text must contain at least 10 words',
                'plagiarism_score': 0,
                'status': 'insufficient_text'
            }), 400
        
        # Check plagiarism
        report = plagiarism_checker.check_text_plagiarism(text, check_mode=check_mode)
        
        return jsonify(report)
        
    except Exception as e:
        return jsonify({'error': f'Plagiarism check failed: {str(e)}'}), 500

@app.route('/api/check-plagiarism-file', methods=['POST'])
def api_check_plagiarism_file():
    """
    API endpoint for plagiarism detection from uploaded files (PDF, Word, PowerPoint, Text)
    """
    temp_path = None
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'File is required'}), 400

        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        check_mode = request.form.get('check_mode', 'advanced')
        
        # Validate file extension
        allowed_extensions = {'.pdf', '.docx', '.pptx', '.txt', '.text', '.doc'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            return jsonify({
                'error': f'Unsupported file format. Allowed: PDF, Word (.docx), PowerPoint (.pptx), Text (.txt)'
            }), 400

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            temp_path = temp_file.name
        
        file.save(temp_path)

        # Check plagiarism
        report = plagiarism_checker.check_file_plagiarism(temp_path, check_mode=check_mode)
        
        return jsonify(report)
        
    except Exception as e:
        return jsonify({'error': f'File plagiarism check failed: {str(e)}'}), 500
    finally:
        # Clean up temporary file
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except Exception:
                pass

@app.route('/api/automation-workflow', methods=['POST'])
def api_automation_workflow():
    """
    API endpoint for end-to-end workflow automation:
    text/file -> summarize -> translate -> speech -> email
    """
    temp_path = None
    try:
        input_mode = request.form.get('input_mode', 'text').strip().lower()
        input_text = request.form.get('text', '').strip()

        sender_email = request.form.get('sender_email', '').strip()
        sender_password = request.form.get('sender_password', '').strip()
        receiver_email = request.form.get('receiver_email', '').strip()
        subject = request.form.get('subject', 'Automated AI Content').strip() or 'Automated AI Content'

        summary_length = request.form.get('summary_length', 'medium').strip()
        summary_style = request.form.get('summary_style', 'paragraph').strip()
        target_language = request.form.get('target_language', 'en').strip()
        run_translate = request.form.get('run_translate', 'true').strip().lower() in ('1', 'true', 'yes', 'on')

        run_plagiarism = request.form.get('run_plagiarism', 'false').strip().lower() in ('1', 'true', 'yes', 'on')
        plagiarism_mode = request.form.get('plagiarism_mode', 'advanced').strip()

        file_path = None
        if input_mode == 'file':
            if 'file' not in request.files:
                return jsonify({'success': False, 'error': 'File is required for file mode'}), 400

            uploaded = request.files['file']
            if uploaded.filename == '':
                return jsonify({'success': False, 'error': 'No file selected'}), 400

            allowed_extensions = {'.pdf', '.docx', '.pptx', '.txt', '.text'}
            file_ext = os.path.splitext(uploaded.filename)[1].lower()
            if file_ext not in allowed_extensions:
                return jsonify({'success': False, 'error': 'Unsupported file format. Allowed: PDF, DOCX, PPTX, TXT'}), 400

            with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
                temp_path = temp_file.name

            uploaded.save(temp_path)
            file_path = temp_path
        else:
            if not input_text:
                return jsonify({'success': False, 'error': 'Text is required in text mode'}), 400

        result = workflow_automation.run_workflow(
            input_text=input_text,
            file_path=file_path,
            summary_length=summary_length,
            summary_style=summary_style,
            target_language=target_language,
            run_translate=run_translate,
            sender_email=sender_email,
            sender_password=sender_password,
            receiver_email=receiver_email,
            subject=subject,
            run_plagiarism=run_plagiarism,
            plagiarism_mode=plagiarism_mode,
        )

        if result.get('success'):
            return jsonify(result)

        return jsonify(result), 500

    except Exception as e:
        return jsonify({'success': False, 'error': f'Automation workflow failed: {str(e)}'}), 500
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except Exception:
                pass


@app.route('/api/workflow-composer', methods=['POST'])
def api_workflow_composer():
    """
    API endpoint for modular workflow composition.
    Supports optional file input and ordered steps:
      - summarize
      - translate
      - text_to_speech
      - email
    """
    temp_path = None
    temp_audio_path = None
    try:
        input_text = ''
        steps = []

        if request.is_json:
            data = request.get_json(silent=True) or {}
            input_text = (data.get('text', '') or '').strip()
            steps = data.get('steps', []) or []
            summary_length = data.get('summary_length', 'medium')
            summary_style = data.get('summary_style', 'paragraph')
            target_language = data.get('target_language', 'en')
            tts_language = data.get('tts_language', target_language)
            send_email_step = bool(data.get('send_email', False))
            sender_email = (data.get('sender_email', '') or '').strip()
            sender_password = (data.get('sender_password', '') or '').strip()
            receiver_email = (data.get('receiver_email', '') or '').strip()
            email_subject = (data.get('subject', 'AutoComm Workflow Output') or 'AutoComm Workflow Output').strip()
        else:
            input_text = (request.form.get('text', '') or '').strip()
            steps = request.form.getlist('steps')
            summary_length = request.form.get('summary_length', 'medium')
            summary_style = request.form.get('summary_style', 'paragraph')
            target_language = request.form.get('target_language', 'en')
            tts_language = request.form.get('tts_language', target_language)
            send_email_step = request.form.get('send_email', 'false').lower() in ('1', 'true', 'yes', 'on')
            sender_email = (request.form.get('sender_email', '') or '').strip()
            sender_password = (request.form.get('sender_password', '') or '').strip()
            receiver_email = (request.form.get('receiver_email', '') or '').strip()
            email_subject = (request.form.get('subject', 'AutoComm Workflow Output') or 'AutoComm Workflow Output').strip()

            uploaded = request.files.get('file')
            if uploaded and uploaded.filename:
                file_ext = os.path.splitext(uploaded.filename)[1].lower()
                allowed_extensions = {'.pdf', '.docx', '.pptx', '.txt', '.text', '.md'}
                if file_ext not in allowed_extensions:
                    return jsonify({'error': 'Unsupported file format. Allowed: PDF, DOCX, PPTX, TXT, MD'}), 400
                with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
                    temp_path = temp_file.name
                uploaded.save(temp_path)
                input_text = (plagiarism_checker.extract_text_from_file(temp_path) or '').strip()

        if not input_text:
            return jsonify({'error': 'Provide input text or upload a supported file.'}), 400

        if not steps:
            steps = ['summarize', 'translate', 'text_to_speech']

        valid_steps = {'summarize', 'translate', 'text_to_speech', 'email'}
        steps = [s for s in steps if s in valid_steps]
        if not steps:
            return jsonify({'error': 'No valid steps selected.'}), 400

        current_text = input_text
        outputs = {'original_text': input_text}
        step_results = []

        for step in steps:
            if step == 'summarize':
                current_text = summarizer.summarize(current_text, length=summary_length, style=summary_style)
                outputs['summary'] = current_text
                step_results.append({'step': 'summarize', 'status': 'done', 'characters': len(current_text)})

            elif step == 'translate':
                normalized_target = (target_language or 'en').split('-')[0].lower()
                current_text = translator.translate(current_text, source_lang='auto', target_lang=normalized_target)
                outputs['translated_text'] = current_text
                outputs['target_language'] = target_language
                step_results.append({'step': 'translate', 'status': 'done', 'target_language': target_language})

            elif step == 'text_to_speech':
                temp_audio_path = text_to_speech.convert_text_to_speech(
                    current_text,
                    language=tts_language,
                    translate_before_tts=False,
                )
                output_name = f"workflow_{uuid.uuid4().hex}.mp3"
                output_path = os.path.join('static', 'temp', output_name)
                os.replace(temp_audio_path, output_path)
                temp_audio_path = None
                outputs['audio_url'] = f"/static/temp/{output_name}"
                outputs['tts_language'] = tts_language
                step_results.append({'step': 'text_to_speech', 'status': 'done', 'audio_file': output_name})

            elif step == 'email':
                if send_email_step or ('email' in steps):
                    if not all([sender_email, sender_password, receiver_email]):
                        return jsonify({'error': 'Email credentials and receiver are required for email step.'}), 400

                    attachments = []
                    if outputs.get('audio_url'):
                        attachments.append(os.path.join(app.root_path, outputs['audio_url'].lstrip('/').replace('/', os.sep)))

                    sent = email_service.send_email(
                        sender_email=sender_email,
                        sender_password=sender_password,
                        receiver_email=receiver_email,
                        subject=email_subject,
                        message=current_text,
                        attachments=attachments,
                    )
                    if not sent:
                        return jsonify({'error': 'Email step failed. Please check credentials.'}), 500
                    outputs['email_receiver'] = receiver_email
                    step_results.append({'step': 'email', 'status': 'done', 'receiver': receiver_email})

        history_service.add_item(
            module='workflow-composer',
            title='Workflow run',
            input_preview=input_text[:300],
            output_preview=(current_text or '')[:400],
            metadata={
                'steps': steps,
                'target_language': target_language,
                'tts_language': tts_language,
            },
            user=session.get('user_email', 'anonymous'),
        )

        return jsonify({'success': True, 'steps': step_results, 'outputs': outputs})

    except Exception as e:
        return jsonify({'error': f'Workflow composer failed: {str(e)}'}), 500
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except Exception:
                pass
        if temp_audio_path and os.path.exists(temp_audio_path):
            try:
                os.unlink(temp_audio_path)
            except Exception:
                pass


@app.route('/api/history', methods=['GET', 'POST'])
def api_history():
    """
    API endpoint for listing and creating history items.
    """
    try:
        if request.method == 'GET':
            favorite_only = request.args.get('favorite_only', 'false').lower() in ('1', 'true', 'yes', 'on')
            module = request.args.get('module', '').strip() or None
            user = session.get('user_email', 'anonymous')
            items = history_service.list_items(user=user, module=module, favorite_only=favorite_only)
            return jsonify({'success': True, 'items': items})

        data = request.get_json(silent=True) or {}
        item = history_service.add_item(
            module=(data.get('module', 'general') or 'general').strip(),
            title=(data.get('title', 'Saved Item') or 'Saved Item').strip(),
            input_preview=(data.get('input_preview', '') or '').strip(),
            output_preview=(data.get('output_preview', '') or '').strip(),
            metadata=data.get('metadata', {}) or {},
            user=session.get('user_email', 'anonymous'),
            favorite=bool(data.get('favorite', False)),
        )
        return jsonify({'success': True, 'item': item})

    except Exception as e:
        return jsonify({'error': f'History operation failed: {str(e)}'}), 500


@app.route('/api/history/<int:item_id>/favorite', methods=['POST'])
def api_history_toggle_favorite(item_id):
    """
    Toggle favorite state for a history item.
    """
    try:
        user = session.get('user_email', 'anonymous')
        item = history_service.toggle_favorite(item_id=item_id, user=user)
        if not item:
            return jsonify({'error': 'History item not found'}), 404
        return jsonify({'success': True, 'item': item})
    except Exception as e:
        return jsonify({'error': f'Favorite update failed: {str(e)}'}), 500


@app.route('/api/history/<int:item_id>', methods=['DELETE'])
def api_history_delete(item_id):
    """
    Delete a history item.
    """
    try:
        user = session.get('user_email', 'anonymous')
        deleted = history_service.delete_item(item_id=item_id, user=user)
        if not deleted:
            return jsonify({'error': 'History item not found'}), 404
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': f'Delete failed: {str(e)}'}), 500

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