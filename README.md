# AutoComm – AI-Powered Communication and Content Automation Suite

![AutoComm Logo](https://img.shields.io/badge/AutoComm-AI%20Powered-blue?style=for-the-badge&logo=robot)

A comprehensive web-based AI platform that integrates multiple communication and content automation features including text summarization, language translation, speech processing, and intelligent email automation.

## 🚀 Features

### 📄 Text Summarization

- **AI-Powered Summarization**: Uses Hugging Face Transformers (BART, DistilBART)
- **Multiple Summary Lengths**: Short, Medium, Long options
- **Smart Text Processing**: Handles long documents with intelligent chunking
- **Fallback Algorithm**: Built-in extraction-based summarization when AI models fail

### 🌍 Language Translation

- **Multi-Language Support**: 12+ languages including English, Spanish, French, German, etc.
- **AI Translation**: Powered by Helsinki-NLP models
- **Auto-Detection**: Automatic source language detection
- **Fallback Translation**: Word-by-word translation for common phrases

### 🎤 Speech-to-Text

- **Audio File Support**: WAV, MP3, M4A formats
- **Multiple Recognition Engines**: Google Speech API, CMU Sphinx
- **Language Selection**: 12+ language variants
- **High Accuracy**: Advanced noise handling and audio preprocessing

### 🔊 Text-to-Speech

- **Natural Voice Generation**: Google Text-to-Speech (gTTS)
- **Multi-Language Voices**: Support for 25+ languages
- **Speed Control**: Normal and slow speech options
- **Audio Download**: MP3 format output with download capability

### 📧 Email Automation

- **SMTP Integration**: Works with Gmail, Yahoo, Outlook
- **Professional Templates**: Meeting requests, follow-ups, introductions
- **Security**: App password support for secure authentication
- **Email Preview**: Review before sending

## 🛠 Tech Stack

### Backend

- **Framework**: Python Flask 3.0
- **AI/ML**: Hugging Face Transformers, PyTorch
- **Speech**: SpeechRecognition, gTTS, PyAudio
- **Email**: SMTP, secure email handling

### Frontend

- **UI Framework**: Bootstrap 5.3
- **Styling**: Custom CSS with modern design
- **JavaScript**: Vanilla JS with advanced features
- **Icons**: Font Awesome 6.0
- **Responsive**: Mobile-first design

### Architecture

```
AutoComm/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── services/             # AI service modules
│   ├── summarizer.py     # Text summarization logic
│   ├── translator.py     # Translation service
│   ├── speech_to_text.py # Speech recognition
│   ├── text_to_speech.py # Voice synthesis
│   └── email_service.py  # Email automation
├── templates/            # HTML templates
│   ├── index.html        # Home page
│   ├── summarizer.html   # Summarization interface
│   ├── translator.html   # Translation interface
│   ├── speech.html       # Speech processing
│   └── email.html        # Email automation
└── static/              # Static assets
    ├── css/
    │   └── style.css     # Custom styles
    └── js/
        └── main.js       # JavaScript functionality
```

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd AutoComm
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv autocomm_env
autocomm_env\Scripts\activate

# Linux/macOS
python3 -m venv autocomm_env
source autocomm_env/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: System-Specific Setup

#### Windows

```bash
# Install Microsoft C++ Build Tools (if not already installed)
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# For PyAudio (if pip install fails):
pip install pipwin
pipwin install pyaudio
```

#### Linux/Ubuntu

```bash
sudo apt-get update
sudo apt-get install portaudio19-dev python3-pyaudio
sudo apt-get install ffmpeg
```

#### macOS

```bash
brew install portaudio
brew install ffmpeg
```

## 🚀 Running the Application

### Development Mode

```bash
python app.py
```

The application will start at: **http://localhost:5000**

### Production Mode

```bash
# Set environment variables
export FLASK_ENV=production
export FLASK_DEBUG=False

# Run with Gunicorn (install: pip install gunicorn)
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 📱 Usage Guide

### 1. Text Summarization

1. Navigate to `/summarizer`
2. Enter text (minimum 100 characters)
3. Select summary length and style
4. Click "Generate Summary"
5. Copy or download the result

### 2. Language Translation

1. Go to `/translator`
2. Select source and target languages
3. Enter text to translate
4. Click "Translate Text"
5. Copy the translation

### 3. Speech Processing

#### Speech-to-Text

1. Visit `/speech`
2. Select "Speech to Text" tab
3. Choose language and upload audio file
4. Click "Convert Speech to Text"
5. View and download transcription

#### Text-to-Speech

1. Select "Text to Speech" tab
2. Enter text and choose language
3. Click "Generate Speech"
4. Play or download audio file

### 4. Email Automation

1. Navigate to `/email`
2. Enter email credentials (use app passwords for Gmail)
3. Fill recipient details and subject
4. Compose message or use templates
5. Preview and send email

## 🔧 Configuration

### Gmail Setup (Recommended)

1. Enable 2-Factor Authentication
2. Go to Google Account Settings → Security
3. Generate App Password
4. Use app password in the email form

### Environment Variables (Optional)

Create a `.env` file:

```env
FLASK_SECRET_KEY=your-secret-key
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

## 🎯 API Endpoints

| Endpoint              | Method | Description                 |
| --------------------- | ------ | --------------------------- |
| `/`                   | GET    | Home page                   |
| `/summarizer`         | GET    | Summarization interface     |
| `/translator`         | GET    | Translation interface       |
| `/speech`             | GET    | Speech processing interface |
| `/email`              | GET    | Email automation interface  |
| `/api/summarize`      | POST   | Text summarization API      |
| `/api/translate`      | POST   | Translation API             |
| `/api/speech-to-text` | POST   | Speech recognition API      |
| `/api/text-to-speech` | POST   | Voice synthesis API         |
| `/api/send-email`     | POST   | Email sending API           |

## 📊 Example API Usage

### Text Summarization

```javascript
fetch("/api/summarize", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    text: "Your long text here...",
  }),
})
  .then((response) => response.json())
  .then((data) => console.log(data.summary));
```

### Language Translation

```javascript
fetch("/api/translate", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    text: "Hello world",
    source_language: "en",
    target_language: "es",
  }),
})
  .then((response) => response.json())
  .then((data) => console.log(data.translation));
```

## 🚨 Troubleshooting

### Common Issues

#### 1. PyAudio Installation Failed

```bash
# Windows
pip install pipwin
pipwin install pyaudio

# Linux
sudo apt-get install portaudio19-dev
```

#### 2. Transformers Model Download Slow

```bash
# Set Hugging Face cache directory
export HF_HOME=/path/to/cache
```

#### 3. Gmail Authentication Error

- Use App Password instead of regular password
- Enable 2-Factor Authentication
- Check "Less secure app access" settings

#### 4. Speech Recognition Not Working

- Check microphone permissions
- Ensure audio file format is supported
- Verify internet connection for Google Speech API

### Performance Tips

1. **First Run**: Initial model downloads may take time
2. **Memory Usage**: Large language models require 2-4GB RAM
3. **Internet**: Some features require internet connection
4. **File Limits**: Audio files limited to 10MB

## 🔒 Security Features

- **Input Validation**: All user inputs are sanitized
- **File Size Limits**: Maximum upload sizes enforced
- **CSRF Protection**: Built-in Flask security
- **Secure Email**: App password authentication
- **Error Handling**: Comprehensive error management

## 🎨 Customization

### Styling

- Modify `static/css/style.css` for custom themes
- Update color variables in CSS root
- Add custom animations and effects

### Features

- Add new AI models in service modules
- Extend API endpoints in `app.py`
- Create new templates for additional features

## 📈 Performance Monitoring

### Logs

Application logs are displayed in console:

- ✅ Success operations
- ⚠️ Warnings and fallbacks
- ❌ Errors and failures

### Metrics

Monitor these key metrics:

- Response times for AI operations
- Memory usage for model loading
- API success/failure rates

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Hugging Face**: For transformer models
- **Google**: For Speech and TTS APIs
- **Bootstrap**: For UI framework
- **Flask**: For web framework
- **Font Awesome**: For icons

## 📞 Support

For support and questions:

- Create an issue on GitHub
- Check troubleshooting section
- Review API documentation

---

**Built with ❤️ and AI** | AutoComm © 2024

### 🚀 Quick Start Summary

```bash
git clone <repo>
cd AutoComm
python -m venv env
env\Scripts\activate  # Windows
pip install -r requirements.txt
python app.py
# Visit: http://localhost:5000
```
