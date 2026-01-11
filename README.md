# 🤖 py_JobAutomation

> **AI-powered job application automation system**
> Canlı sürüm: https://py-jobautomation.onrender.com

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2.7-green.svg)](https://www.djangoproject.com/)
[![Tests](https://img.shields.io/badge/Tests-62%20passed-brightgreen.svg)]()

## ✨ Features

- 🤖 **AI-Powered Job Matching** - Smart CV-job analysis with contextual scoring
- 📄 **CV Management** - Multi-profile CV system with AI import
- ✍️ **Automated Cover Letters** - German Anschreiben generation
- 🔐 **User Authentication** - Secure login/registration system
- 🛡️ **Fallback System** - Works even when AI is unavailable
- 📊 **Application History** - Track all job applications

## 🛠️ Tech Stack

- **Backend**: Django 5.2.7, Python 3.13
- **AI**: OpenAI, Google Gemini, Groq
- **Database**: SQLite
- **Frontend**: Bootstrap 5, Font Awesome
- **Testing**: pytest, coverage
- **Containerization**: Docker, Docker Compose

## 🚀 Quick Start

### 1️⃣ Clone & Setup

```bash
git clone https://github.com/mhilmicicek07/py_JobAutomation.git
cd py_JobAutomation
```

### 2️⃣ Using Virtual Environment (Optional, Local)

```bash
python -m venv venv
# Windows  
venv\Scripts\activate
# Linux / Mac
# source venv/bin/activate
pip install -r requirements.txt
cp env.example .env
python manage.py migrate
python manage.py createsuperuser
pytest
python manage.py runserver
```

### 3️⃣ Using Docker (Recommended)

```bash
docker compose build --no-cache
docker compose up -d
docker compose logs -f web
```

Web servisi http://localhost:8000 üzerinde çalışıyor
Worker timeout uyarıları olabilir; deploy sırasında --timeout parametresiyle ayarlanabilir

## 📖 Usage

1. **Register/Login**: Create account or sign in
2. **Configure AI**: Add API key for AI features (optional)
3. **Create CV**: Build your CV profile
4. **Job Analysis**: Paste job posting, get AI match score
5. **Cover Letter**: Automatic German Anschreiben generation

## 🤖 AI Setup (Optional)

For AI features, get API key from:
- OpenAI: https://platform.openai.com/api-keys
- Google Gemini: https://aistudio.google.com
- Groq: https://console.groq.com

⚠️ Note: The google.generativeai package is deprecated. Use google.genai instead.

Add key to `/ai/settings/` after login.

## 🧪 Testing

```bash
pytest  # Run all tests
pytest --cov=. --cov-report=html  # With coverage
```

## 📁 Architecture

```
py_JobAutomation/
├── users/              # Authentication
├── cv_manager/         # CV management
├── job_analyzer/       # Job matching
├── ai_bridge/          # AI integration
├── applicant_letters/  # Cover letters
└── templates/          # HTML templates
```

## 📜 License

MIT License

## 👨‍💻 Developer

**Mehmet Hilmi Çiçek**

- GitHub: [@mhilmicicek07](https://github.com/mhilmicicek07)
- Email: m.hilmicicek07@gmail.com
- LinkedIn: [@mhilmicicek](https://linkedin.com/in/mhilmicicek)