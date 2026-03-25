# AutoComm - Architecture Diagrams & Reference Guide

## Quick Architecture Visualizations

### 1. System Layers (Layered Architecture)

```
┌─────────────────────────────────────────────────────────────┐
│                PRESENTATION LAYER                           │
│  Jinja2 Templates, HTML, CSS, Vanilla JavaScript, Bootstrap│
│  (User Interface - Web Browser)                            │
└─────────────────────────────────────────────────────────────┘
                          ↕ HTTP/REST
┌─────────────────────────────────────────────────────────────┐
│              APPLICATION LAYER (Flask)                      │
│  • Routing & Request Handling                              │
│  • Session Management & Authentication                     │
│  • Request Validation & Response Formatting               │
│  • Business Logic Orchestration                           │
└─────────────────────────────────────────────────────────────┘
                          ↕ Function Calls
┌─────────────────────────────────────────────────────────────┐
│               SERVICE LAYER                                 │
│  • TextSummarizer (BART/DistilBART)                        │
│  • LanguageTranslator (Google Translate)                  │
│  • SpeechToTextConverter (Google Speech API)              │
│  • TextToSpeechConverter (gTTS)                           │
│  • EmailService (SMTP)                                    │
│  • PlagiarismChecker (scikit-learn)                       │
│  • WorkflowAutomationService (Orchestrator)               │
└─────────────────────────────────────────────────────────────┘
                          ↕ Library Calls
┌─────────────────────────────────────────────────────────────┐
│              INTEGRATION LAYER                              │
│  Open-source libraries & SDKs                              │
│  • Hugging Face Transformers, PyTorch                      │
│  • deep-translator, SpeechRecognition, gTTS               │
│  • scikit-learn, Pillow, PyPDF2                           │
└─────────────────────────────────────────────────────────────┘
                          ↕ API Calls
┌─────────────────────────────────────────────────────────────┐
│              EXTERNAL SERVICES LAYER                        │
│  Cloud APIs & 3rd-party services                           │
│  • Hugging Face Model Hub                                  │
│  • Google Cloud APIs (Translate, Speech-to-Text)          │
│  • SMTP Providers (Gmail, Outlook, Yahoo)                 │
│  • CDN (Bootstrap, FontAwesome, Google Fonts)             │
└─────────────────────────────────────────────────────────────┘
```

---

### 2. Service Communication Patterns

#### Pattern A: Direct Request (Single Service)

```
User Request
    ↓
Flask Route
    ↓
Service Instance
    ↓
External API (if needed)
    ↓
Response to User
```

#### Pattern B: Composition (Workflow Service)

```
User Request
    ↓
Flask Route
    ↓
WorkflowAutomationService (Orchestrator)
    ├→ TextSummarizer
    ├→ LanguageTranslator
    ├→ TextToSpeechConverter
    ├→ EmailService
    └→ PlagiarismChecker
    ↓
Aggregated Response
    ↓
Response to User
```

#### Pattern C: Fallback Chain (Error Resilience)

```
User Request
    ↓
Primary Service
    ├─ Success? → Return
    └─ Fail?
        ↓
        Fallback Service 1
        ├─ Success? → Return
        └─ Fail?
            ↓
            Fallback Service 2
            ├─ Success? → Return
            └─ Fail?
                ↓
                Return Error (with partial results)
```

---

### 3. Data Flow for Key Request Types

#### Summarization Request Flow

```
TEXT INPUT
    ↓
Frontend: /summarizer.html
    ├─ User enters/uploads text
    ├─ Selects length (short/medium/long)
    ├─ Selects style (paragraph/bullets)
    └─ Clicks "Summarize"
    ↓
fetch('/api/summarize', {...})
    ↓
Flask Route: @app.route('/api/summarize', POST)
    ├─ Validate input (not empty, file size < 16MB)
    ├─ Extract text from request
    └─ Call summarizer.summarize(text, length, style)
    ↓
TextSummarizer Service
    ├─ _ensure_model()
    │  └─ Load BART from Hugging Face (first time only)
    ├─ Truncate/chunk text if needed
    ├─ Tokenize input
    ├─ Run inference on BART model
    └─ Decode output tokens to text
    ↓
Return: {success: true, summary: "..."}
    ↓
Flask: jsonify(result) → JSON response (200 OK)
    ↓
Frontend: Receive JSON response
    ├─ Parse JSON
    ├─ Update DOM with summary
    └─ Display to user

TOTAL FLOW: User Input → Validation → Model Inference → Response → Display
```

#### Email Automation Request Flow

```
USER INPUTS EMAIL DETAILS
    ↓
Frontend: /email.html
    ├─ Sender email, password (app password)
    ├─ Recipient email
    ├─ Subject, message body
    ├─ Optional: Select template
    └─ Click "Send"
    ↓
fetch('/api/send-email', {...})
    ↓
Flask Route: @app.route('/api/send-email', POST)
    ├─ Validate session (user logged in)
    ├─ Validate email format (regex)
    ├─ Extract parameters from request
    └─ Call email_service.send_email(...)
    ↓
EmailService
    ├─ _get_smtp_config(sender_email)
    │  └─ Determine SMTP server (Gmail, Outlook, etc.)
    ├─ _create_message(sender, receiver, subject, body)
    │  └─ Create MIMEMultipart message with headers
    └─ _send_via_smtp(config, sender, password, receiver, msg)
       ├─ smtplib.SMTP(server, port)
       ├─ context.wrap_socket() → SSL/TLS
       ├─ smtp.starttls()
       ├─ smtp.login(sender, password)
       ├─ smtp.send_message(msg)
       └─ smtp.quit() → Close connection
    ↓
SMTP Server (Gmail/Outlook/Yahoo)
    └─ Authenticate & deliver email
    ↓
Return: {success: true, message: "Email sent"}
    ↓
Frontend: Display success message to user

ERROR HANDLING:
- Bad credentials? → Return 401 "Authentication failed"
- SMTP error? → Return 503 "Email service unavailable"
- Invalid email? → Return 400 "Invalid recipient email"
```

#### Workflow (End-to-End) Request Flow

```
WORKFLOW INPUT (Text, Language, Email, etc.)
    ↓
Frontend: /automation.html
    ├─ Upload/paste text
    ├─ Select target language
    ├─ Enable features: plagiarism, email
    ├─ Enter email credentials
    └─ Click "Run Workflow"
    ↓
fetch('/api/workflow', {...})
    ↓
Flask Route: @app.route('/api/workflow', POST)
    ├─ Validate all inputs
    └─ Call workflow_automation.run_workflow(...)
    ↓
WorkflowAutomationService.run_workflow()
    ├─ STEP 1: Extract Text
    │  ├─ From file or direct input
    │  └─ Return: extracted_text
    │
    ├─ STEP 2: Check Plagiarism (if enabled)
    │  ├─ plagiarism_checker.check_plagiarism(text)
    │  └─ Return: similarity_score, is_plagiarized
    │
    ├─ STEP 3: Summarize
    │  ├─ summarizer.summarize(text, length)
    │  └─ Return: summary
    │
    ├─ STEP 4: Translate
    │  ├─ translator.translate(summary, target_lang)
    │  └─ Return: translated_summary
    │
    ├─ STEP 5: Text-to-Speech
    │  ├─ text_to_speech.convert_text_to_speech(translated_summary)
    │  └─ Return: audio_file_path
    │
    └─ STEP 6: Send Email
       ├─ email_service.send_email(
       │     translated_summary,
       │     audio_attachment,
       │     receiver_email
       │  )
       └─ Return: email_sent_status
    ↓
Aggregate Results
    ├─ {
    │   "success": true,
    │   "steps": {
    │     "extract": {...},
    │     "plagiarism": {...},
    │     "summarize": {...},
    │     "translate": {...},
    │     "speech": {...},
    │     "email": {...}
    │   }
    │ }
    └─ Return JSON response
    ↓
Frontend: Process & Display
    ├─ Show step-by-step status
    ├─ Display each output
    ├─ Provide download links
    └─ Show success message

TIMELINE: Extraction ~ 1s → Plagiarism ~ 2-5s → Summarization ~ 3-8s →
          Translation ~ 1-3s → Speech ~ 2-4s → Email ~ 1s = TOTAL ~10-25s
```

---

### 4. Code Organization Map

```
autoComm/
│
├── app.py (Router - 300+ lines)
│   ├── Initialize Flask app
│   ├── Configure settings
│   ├── Instantiate services
│   ├── Auth routes (login, signup, logout)
│   ├── Page routes (HTML rendering)
│   └── API routes (JSON responses)
│
├── services/ (Business Logic - Core)
│   ├── summarizer.py (150+ lines)
│   │   ├── TextSummarizer class
│   │   ├── BART/DistilBART integration
│   │   ├── Extraction-based fallback
│   │   └── Length config management
│   │
│   ├── translator.py (200+ lines)
│   │   ├── LanguageTranslator class
│   │   ├── Google Translate integration
│   │   ├── Language support list
│   │   └── Fallback translation
│   │
│   ├── speech_to_text.py (150+ lines)
│   │   ├── SpeechToTextConverter class
│   │   ├── Google Speech API integration
│   │   ├── Audio preprocessing
│   │   └── Multiple language support
│   │
│   ├── text_to_speech.py (100+ lines)
│   │   ├── TextToSpeechConverter class
│   │   ├── gTTS integration
│   │   ├── Language/speed options
│   │   └── Audio file export
│   │
│   ├── email_service.py (150+ lines)
│   │   ├── EmailService class
│   │   ├── SMTP server detection
│   │   ├── Email template support
│   │   └── Multiple provider support
│   │
│   ├── plagiarism_checker.py (100+ lines)
│   │   ├── PlagiarismChecker class
│   │   ├── TF-IDF similarity scoring
│   │   ├── Multiple check modes
│   │   └── Online verification (optional)
│   │
│   └── workflow_automation.py (200+ lines)
│       ├── WorkflowAutomationService class
│       ├── Service orchestration
│       ├── Step-by-step execution
│       ├── Error recovery
│       └── Result aggregation
│
├── templates/ (UI Layer - HTML)
│   ├── index.html (Dashboard, 100+ lines)
│   ├── summarizer.html (50 lines)
│   ├── translator.html (50 lines)
│   ├── speech.html (50 lines)
│   ├── email.html (50 lines)
│   ├── plagiarism.html (50 lines)
│   ├── automation.html (100+ lines)
│   ├── login.html (50 lines)
│   └── signup.html (50 lines)
│
├── static/ (Frontend Assets)
│   ├── css/
│   │   └── style.css (Custom styling, 100+ lines)
│   └── js/
│       └── main.js (AJAX/DOM logic, 200+ lines)
│
├── requirements.txt (Dependencies)
├── README.md (User documentation)
└── ARCHITECTURE.md (This document)

STRUCTURE SUMMARY:
- Small, focused service classes (~100-200 lines each)
- Clean separation: Services don't import each other
- Services injected into routes (Dependency Injection)
- Orchestrator service composes other services
- No database layer (in-memory sessions)
- No config classes (inline constants)
```

---

### 5. Class Relationships Diagram

```
                          Flask App
                              │
                    ┌─────────┼─────────┐
                    ↓         ↓         ↓
        TextSummarizer  LanguageTranslator  EmailService
                    ↓         ↓         ↓
        SpeechToTextConverter  │    TextToSpeechConverter
                        ↓
                PlagiarismChecker

        All Services Injected Into:
                WorkflowAutomationService
                        ↓
                 Uses all above services
                        ↓
                 Called by /api/workflow route
```

---

### 6. Request Handling Pipeline

```
Incoming HTTP Request
        ↓
Flask Request Routing
    ├─ URL matching
    └─ HTTP method (GET/POST)
        ↓
    Route Handler Function
        ├─ Extract parameters (request.form, request.files)
        ├─ Validate input (file type, size, format)
        └─ Check authentication (session)
        ↓
    Service Call
        ├─ Pass validated data to service
        ├─ Service performs business logic
        └─ Return result or raise exception
        ↓
    Response Processing
        ├─ Success → Prepare JSON/HTML
        └─ Error → Prepare error response
        ↓
    HTTP Response
        ├─ Status code (200, 400, 500, etc.)
        ├─ Headers (Content-Type, etc.)
        └─ Body (JSON or HTML)
        ↓
    Browser/Client
        ├─ Receive response
        ├─ Parse content
        └─ Display to user
```

---

### 7. Technology Integration Points

```
Flask Application
├─→ Hugging Face Hub
│   └─ Download transformers (BART, DistilBART)
│
├─→ Hugging Face Transformers Library
│   ├─ Load models locally
│   ├─ Run inference (summarization, translation)
│   └─ Manage tokenizers
│
├─→ PyTorch (Backend for HF)
│   └─ GPU/CPU tensor operations
│
├─→ deep-translator Library
│   └─→ Google Translate API
│       └─ Real-time translation
│
├─→ SpeechRecognition Library
│   └─→ Google Speech API
│       └─ Audio-to-text conversion
│
├─→ gTTS Library
│   └─→ Google Text-to-Speech API
│       └─ Text-to-audio conversion
│
├─→ scikit-learn
│   └─ TF-IDF vectorization & similarity
│
├─→ smtplib (Python stdlib)
│   └─→ SMTP Providers
│       ├─ Gmail (smtp.gmail.com:587)
│       ├─ Outlook (smtp-mail.outlook.com:587)
│       └─ Yahoo (smtp.mail.yahoo.com:587)
│
├─→ PyPDF2, python-docx, python-pptx
│   └─ Extract text from documents
│
└─→ Jinja2 Template Engine
    ├─ Render HTML with dynamic data
    └─ Pass context to templates
```

---

### 8. Error Handling Architecture

```
User Request → Route Handler
    ├─ Input Validation
    │  ├─ Empty input? → 400
    │  ├─ Invalid format? → 400
    │  ├─ File too large? → 413
    │  └─ Pass → Continue
    │
    ├─ Service Call
    │  ├─ Primary Service succeeds? → Return result
    │  ├─ Primary Service fails?
    │  │  └─ Try Fallback Service
    │  │     ├─ Fallback succeeds? → Return result
    │  │     └─ Fallback fails?
    │  │        └─ Try next fallback
    │  └─ All fail? → Return error
    │
    ├─ Response Packaging
    │  ├─ Success? → {success: true, data: ...}
    │  └─ Error? → {success: false, error: "..."}
    │
    └─ HTTP Response
       ├─ JSON encoded
       ├─ Proper status code
       └─ Error message to user
```

---

### 9. Performance Bottleneck Analysis

```
Request Latency Breakdown (Typical Workflow):

User Input
  ↓ (50ms network latency)
Flask Processing
  ├─ Request parsing: 10ms
  ├─ Validation: 5ms
  └─ Route matching: 2ms
  ↓ (17ms)
Service Execution (MAIN BOTTLENECK)
  ├─ Plagiarism Check: 2-5s (fast)
  ├─ Summarization: 3-8s (slow - model inference)
  ├─ Translation: 1-3s (API call)
  ├─ Text-to-Speech: 2-4s (API call + audio processing)
  └─ Email Send: 1-2s (SMTP)
  ↓ (9-23s)
Response Encoding: 50ms
  ↓ (50ms)
Network Transmission
  ↓ (100-500ms depending on response size)
Frontend Rendering: 50ms
  ↓
User Sees Result

TOTAL: 9-24 seconds
CRITICAL PATH: Summarization (BART inference) - MAIN COST

OPTIMIZATION TARGETS:
1. Model quantization (DistilBART instead of BART)
2. GPU acceleration for inference
3. Async/background processing
4. Response streaming for large outputs
5. Caching of repeated queries
```

---

### 10. Database Schema (Recommended for Production)

```
users
├─ id (PK)
├─ email (UNIQUE)
├─ password_hash
├─ first_name
├─ last_name
├─ created_at
└─ updated_at

workflow_executions
├─ id (PK)
├─ user_id (FK users.id)
├─ input_text
├─ execution_steps (JSON)
│  ├─ extract
│  ├─ plagiarism
│  ├─ summarize
│  ├─ translate
│  ├─ speech
│  └─ email
├─ created_at
└─ status (pending/completed/failed)

api_logs
├─ id (PK)
├─ user_id (FK users.id)
├─ endpoint
├─ method
├─ status_code
├─ response_time_ms
├─ created_at
└─ error_message (nullable)

email_templates
├─ id (PK)
├─ name
├─ subject_template
├─ body_template
└─ created_at
```

---

### 11. Deployment Checklist

```
Pre-Deployment
☐ Unit tests passing
☐ Integration tests passing
☐ Load testing completed
☐ Security audit performed
☐ Dependencies documented
☐ API documentation complete

Development → Staging
☐ Deploy to staging environment
☐ Run smoke tests
☐ Load test (staging traffic volume)
☐ Performance profiling
☐ Security scanning (staging)

Staging → Production
☐ Database migration script tested
☐ Rollback procedure documented
☐ Monitoring/alerting configured
☐ Logging infrastructure set up
☐ CDN cache invalidation planned
☐ Infrastructure capacity verified
☐ On-call schedule established

Post-Deployment
☐ Monitor error rates
☐ Monitor API response times
☐ Monitor background job queues
☐ Monitor model inference times
☐ Monitor SMTP delivery
☐ Verify user experience
☐ Check logs for anomalies
```

---

## Configuration Reference

### Environment Variables

```
FLASK_ENV=production|development
FLASK_DEBUG=0|1
SECRET_KEY=your-secret-key
MAX_CONTENT_LENGTH=16777216  # 16MB in bytes
UPLOAD_FOLDER=/path/to/uploads

# Optional: API Keys (for paid services)
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AIza...
AZURE_SPEECH_KEY=...

# Model Configuration
TRANSFORMER_MODEL=facebook/bart-large-cnn
USE_GPU=True|False
MODEL_CACHE_DIR=~/.cache/huggingface/

# Email Configuration
SMTP_DEFAULT_TIMEOUT=15
EMAIL_MAX_RETRIES=3

# Logging
LOG_LEVEL=INFO|DEBUG
LOG_FILE=/var/log/autocomm/app.log
```

---

## Troubleshooting Guide

| Issue                    | Root Cause             | Solution                                   |
| ------------------------ | ---------------------- | ------------------------------------------ |
| Slow summarization       | Model loading overhead | Use DistilBART or enable GPU               |
| Translation timeout      | API rate limit         | Implement request queue/backoff            |
| Email send failure       | SMTP auth error        | Verify app password, not regular password  |
| Speech recognition fails | Audio quality          | Check audio format, try WAV instead of MP3 |
| OOM on summarization     | Model too large        | Switch to smaller model (DistilBART)       |
| 503 Service Unavailable  | External API down      | Use fallback service                       |

---

## Summary

**AutoComm** uses a **layered, service-oriented architecture** with clear separation of concerns. The design emphasizes:

✅ **Modularity**: Each service is independent  
✅ **Resilience**: Fallback strategies for every operation  
✅ **Scalability**: Stateless design, easy to distribute  
✅ **Maintainability**: Clean code, focused classes  
✅ **Extensibility**: Easy to add new services/features

This architecture supports rapid development, easy testing, and straightforward deployment to production environments.
