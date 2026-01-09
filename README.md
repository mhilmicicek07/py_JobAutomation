# 🤖 py_JobAutomation

> **Django-basiertes System zur Automatisierung von Bewerbungsprozessen**  
> Yapay zeka destekli iş başvuru otomasyonu (Almanca Anschreiben üretimi, CV yönetimi, ilan analizi)

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2.7-green.svg)](https://www.djangoproject.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/Tests-62%20passed-brightgreen.svg)](https://github.com/mhilmicicek07/py_JobAutomation/actions)
[![Coverage](https://img.shields.io/badge/Coverage-68%25-brightgreen.svg)](htmlcov/index.html)
[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2.7-green.svg)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 İçindekiler

- [Özellikler](#-özellikler)
- [Teknoloji Stack](#-teknoloji-stack)
- [Hızlı Başlangıç](#-hızlı-başlangıç)
- [Environment Variables](#-environment-variables)
- [AI Konfigürasyonu](#-ai-konfigürasyonu)
- [Kullanım](#-kullanım)
- [API Reference](#-api-reference)
- [Testler](#-testler)
- [Deployment](#-deployment)
- [Troubleshooting](#-troubleshooting)
- [Güvenlik](#-güvenlik)
- [Proje Yapısı](#-proje-yapısı)
- [Changelog](#-changelog)
- [Katkıda Bulunma](#-katkıda-bulunma)

---

## ✨ Özellikler

### 🔐 Kullanıcı Yönetimi (`users`)
- ✅ **Django Authentication**: Kayıt, giriş, çıkış sistemi
- ✅ **User Isolation**: Her kullanıcı sadece kendi verilerini görür
- ✅ **Session Management**: Güvenli oturum yönetimi
- ✅ **CSRF Protection**: Form güvenliği

### 📄 CV Yönetimi (`cv_manager`)
- ✅ **Çoklu CV Profili**: Web/IT, BWL/Finance, Genel kategoriler
- ✅ **Detaylı CV Studio**: Kişisel bilgiler, deneyim, eğitim, beceriler, diller
- ✅ **AI CV Import**: Ham metin → Yapılandırılmış veri (GPT-4o/Gemini/Groq)
- ✅ **Skill Management**: Otomatik beceri gruplandırma (MS Office, IT Tools)
- ✅ **Language Proficiency**: CEFR standartlarında dil seviyeleri
- ✅ **Process Tracking**: Çalışma izni, istifa, ehliyet süreçleri

### 🔍 İlan Analizi (`job_analyzer`)
- ✅ **AI-Powered CV-Job Matching**: Tam bağlamsal karşılaştırma
  - Deneyim değerlendirmesi (yıllar, sektör)
  - Eğitim uygunluğu
  - Beceri eşleşmesi
  - Dil seviyesi kontrolü
- ✅ **Smart Scoring Algorithm**: 0-100 arası gerçekçi skorlama
- ✅ **Intelligent Decision Making**:
  - **APPLY** (≥80): Kesin başvur
  - **REVIEW** (≥50): Değerlendirilmeli
  - **SKIP** (<50): Başvurma
- ✅ **Fallback System**: AI başarısız olursa heuristic parser
- ✅ **Dynamic CV Selection**: CV sayısı otomatik alan seçimi
- ✅ **Application History**: Geçmiş başvurular ve detaylar

### ✍️ Başvuru Mektubu (`applicant_letters`)
- ✅ **AI Anschreiben Generation**: Kişiselleştirilmiş Almanca mektup
- ✅ **ATS-Compatible CV Sections**: Profil, Kenntnisse, Erfahrung bölümleri
- ✅ **Template Fallback**: AI çalışmazsa hazır şablonlar
- ✅ **Positive Language AI**: Eksiklikleri negatif sunmadan vurgular
- ✅ **Draft Management**: Taslak kaydetme ve düzenleme

### 🧠 AI Entegrasyonu (`ai_bridge`)
- ✅ **Multi-Provider Support**: OpenAI, Google Gemini, Groq
- ✅ **User-Specific API Settings**: Her kullanıcı kendi API key'i
- ✅ **Automatic Encryption**: Fernet ile API key şifreleme
- ✅ **Provider Fallback**: Ana provider başarısız olursa otomatik geçiş
- ✅ **Cost Optimization**: Model seçimi ve token yönetimi
- ✅ **Error Handling**: Ağ sorunları, rate limits, API hataları

---

## 🛠 Teknoloji Stack

| Kategori | Teknolojiler |
|----------|-------------|
| **Backend** | Django 5.2.7, Python 3.13 |
| **Database** | SQLite (dev), PostgreSQL (production) |
| **AI/ML** | OpenAI API, Google Gemini, Groq |
| **Frontend** | Bootstrap 5.3, Font Awesome 6.x |
| **Security** | Fernet Encryption, CSRF Protection, User Authentication |
| **Testing** | pytest 7.4+, pytest-django 4.5+, pytest-cov 4.1+ |
| **Code Quality** | Black, Flake8, isort |
| **Deployment** | Gunicorn, Nginx, Docker (optional) |
| **Environment** | python-decouple, python-dateutil |

---

## 🚀 Hızlı Başlangıç

### ⚡ 5 Dakikada Çalışır Hale Getirme

```bash
# 1. Projeyi klonlayın
git clone https://github.com/mhilmicicek07/py_JobAutomation.git
cd py_JobAutomation

# 2. Virtual environment oluşturun
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# 3. Bağımlılıkları yükleyin
pip install -r requirements.txt

# 4. Environment variables ayarlayın
cp env.example .env
# .env dosyasını düzenleyin (SECRET_KEY zorunlu)

# 5. Veritabanı migrasyonu
python manage.py migrate

# 6. Süper kullanıcı oluşturun
python manage.py createsuperuser

# 7. Testleri çalıştırın
pytest

# 8. Sunucuyu başlatın
python manage.py runserver

# 9. Tarayıcıda açın: http://127.0.0.1:8000
```

### 📋 Gereksinimler
- **Python 3.13+**
- **Git**
- **Virtual Environment** (venv)
- **AI API Key** (OpenAI/Gemini/Groq)

---

## ⚙️ Environment Variables

### Temel Ayarlar
```bash
# Django Core
SECRET_KEY=your-super-secret-key-here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Database (Production)
DATABASE_URL=postgres://user:password@localhost:5432/dbname
```

### AI Konfigürasyonu
```bash
# Global AI Provider (kullanıcı ayarları önceliklidir)
AI_PROVIDER=openai

# OpenAI Models
OPENAI_DEFAULT_MODEL=gpt-4o-mini
OPENAI_MODEL_CV=gpt-4o-mini
OPENAI_MODEL_POSTING=gpt-4o-mini
OPENAI_MODEL_LETTER=gpt-4o-mini

# Cover Letter Provider
AI_COVER_LETTER_PROVIDER=openai
```

### İş Eşleştirme Eşikleri
```bash
JOB_MATCH_THRESHOLD_APPLY=80    # ≥80: APPLY
JOB_MATCH_THRESHOLD_REVIEW=50   # ≥50: REVIEW
                                  # <50: SKIP
```

### Production Güvenlik
```bash
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
```

---

## 🚀 Kurulum

### 1. Gereksinimler
```bash
# Python 3.13 yüklü olmalı
python --version  # >= 3.13
```

### 2. Projeyi Klonlayın
```bash
git clone https://github.com/mhilmicicek07/py_JobAutomation.git
cd py_JobAutomation
```

### 3. Virtual Environment Oluşturun
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Bağımlılıkları Yükleyin
```bash
pip install -r requirements.txt
```

### 5. Environment Variables Ayarlayın
```bash
# env.example dosyasını kopyalayın
cp env.example .env

# .env dosyasını düzenleyin:
SECRET_KEY=your-django-secret-key-here
DEBUG=True
```

### 6. Veritabanı Migration
```bash
python manage.py migrate
```

### 7. Superuser Oluşturun
```bash
python manage.py createsuperuser
```

### 8. Sunucuyu Başlatın
```bash
python manage.py runserver
```

📍 Tarayıcıda `http://127.0.0.1:8000` adresine gidin.

---

## ⚠️ **Önemli: AI API Anahtarı Gereklidir**

Bu uygulamanın temel özelliklerini (CV import, iş analizi, otomatik mektup oluşturma) kullanabilmek için **AI API anahtarı** gereklidir:

1. **OpenAI** (Önerilen): Ücretsiz $5 kredi ile başlayın
2. **Google Gemini**: Ücretsiz kota
3. **Groq**: Çok hızlı, açık kaynak modeller

Giriş yaptıktan sonra **"Einstellungen"** menüsünden API anahtarınızı ayarlayın.

---

## 🔐 AI Konfigürasyonu

> ⚠️ **API Anahtarı olmadan AI özellikler çalışmaz!** CV import, iş analizi ve otomatik mektup üretimi için API anahtarı zorunludur.

### Kullanıcı Ayarları (Önerilen Yöntem)

1. **Giriş yapın** ve `/ai/settings/` adresine gidin
2. **AI Sağlayıcı** seçin:
   - **OpenAI**: GPT-4o-mini (en kararlı sonuçlar)
   - **Gemini**: Google AI, hızlı ve ücretsiz quota
   - **Groq**: Çok hızlı, açık kaynak modeller (Llama3)
3. **API Key** girin:
   - OpenAI: `sk-...` ([platform.openai.com](https://platform.openai.com/api-keys))
   - Gemini: `AIza...` ([aistudio.google.com](https://aistudio.google.com/))
   - Groq: `gsk_...` ([console.groq.com](https://console.groq.com/))
4. **Model** (opsiyonel):
   - OpenAI: `gpt-4o-mini`, `gpt-4o`, `gpt-4-turbo`
   - Gemini: `gemini-1.5-flash`, `gemini-1.5-pro`
   - Groq: `llama-3.3-70b-versatile`, `mixtral-8x7b-32768`

### Güvenlik
- ✅ API key'ler **otomatik şifrelenir** (Fernet encryption)
- ✅ Veritabanında **plain text saklanmaz**
- ✅ Her kullanıcı **kendi key'ini** kullanır
- ⚠️ `.env` dosyasını **asla** git'e eklemeyin!

---

## 📖 Kullanım

### 1. Kullanıcı Kaydı ve Giriş

- **Kayıt**: `/users/register/` sayfasından hesap oluşturun
- **Giriş**: `/users/login/` ile oturum açın
- **Güvenlik**: Her kullanıcı kendi verilerini görür

### 2. AI Ayarları Yapılandırma

**"Einstellungen"** menüsünden:
1. AI Sağlayıcı seçin (OpenAI, Gemini, Groq)
2. API anahtarınızı girin
3. Model seçin (opsiyonel - varsayılan kullanılır)

### 3. CV Oluşturma

**Dashboard** → **Neuen CV anlegen**
- İsim, alan (Web/BWL/Genel), iletişim bilgileri girin
- **AI Import** ile ham CV metnini yapılandırılmış veriye çevirin
- Eğitim, deneyim, beceriler, diller ekleyin

### 4. Hızlı Başvuru (AI-Powered)

**Schnellbewerbung** menüsünden:
1. İlan metnini yapıştırın
2. **CV alanı otomatik seçilir** (1 CV varsa gizli, çok CV varsa görünür)
3. **Analysieren** tıklayın
4. **AI Tam Karşılaştırma**:
   - 🎯 **Gerçekçi Match Score** (0-100): Bağlam, deneyim, eğitim değerlendirmesi
   - 📊 **Detaylı Reasoning**: Neden bu skor? Eksiklikler neler?
   - 🤖 **AI Karar**: APPLY/REVIEW/SKIP
   - ⚡ **Fallback Sistemi**: AI çalışmazsa otomatik heuristic yedek
5. **Otomatik Üretim**:
   - ✉️ **Anschreiben**: Hazır Almanca ön yazı
   - 📄 **CV Blöcke**: ATS uyumlu kopyala-yapıştır bölümleri

### 5. Başvuru Geçmişi

**Historie** menüsünden:
- Kullanıcının kendi başvuruları listesi
- Her başvurunun detaylarına tıklayarak görüntüleme
- Anschreiben ve CV bölümlerini tekrar inceleme

---

## 🧪 Testler

### Tüm Testleri Çalıştırma
```bash
pytest
```

### Kapsam Raporu
```bash
pytest --cov=. --cov-report=html
```

### Modül Bazlı Test
```bash
pytest cv_manager/tests.py
pytest job_analyzer/tests.py
pytest ai_bridge/tests.py
pytest applicant_letters/tests.py
```

### Beklenen Sonuçlar
- ✅ 50+ test case
- ✅ %80+ kod kapsamı
- ✅ Model, view, servis testleri

---

## 📁 Proje Yapısı

```
py_JobAutomation/
├── cv_manager/          # CV yönetim modülü
│   ├── models.py        # CV, Skill, Experience, Education, Language
│   ├── views.py         # Dashboard, CRUD işlemleri
│   ├── forms.py         # Django form tanımları
│   ├── urls.py          # URL routing
│   └── tests.py         # Unit testler
│
├── job_analyzer/        # İlan analiz motoru
│   ├── models.py        # JobPosting modeli
│   ├── views.py         # Schnellbewerbung view
│   ├── services.py      # Heuristic parser, skorlama
│   └── tests.py         # Servis testleri
│
├── ai_bridge/           # AI entegrasyon katmanı
│   ├── models.py        # UserAISettings, ExtractionSnapshot
│   ├── providers.py     # OpenAI/Gemini/Groq provider'ları
│   ├── services.py      # AI extraction servisleri
│   ├── encryption.py    # API key şifreleme
│   ├── views.py         # Ayarlar sayfası
│   └── tests.py         # Provider testleri
│
├── applicant_letters/   # Anschreiben üretimi
│   ├── models.py        # ApplicationDraft
│   ├── services.py      # Cover letter builder
│   └── tests.py         # Letter generation testleri
│
├── templates/           # HTML şablonları
│   ├── base.html        # Ana layout
│   └── [app_templates]  # App-specific templates
│
├── py_JobAutomation/    # Django proje ayarları
│   ├── settings.py      # Genel konfigürasyon
│   └── urls.py          # Root URL conf
│
├── requirements.txt     # Python bağımlılıkları
├── env.example          # Örnek environment dosyası
├── .gitignore           # Git ignore kuralları
└── README.md            # Bu dosya
```

---

## 🔌 API Reference

### REST API Endpoints

#### Authentication
- `POST /users/login/` - Kullanıcı girişi
- `POST /users/logout/` - Kullanıcı çıkışı
- `POST /users/register/` - Yeni kullanıcı kaydı

#### CV Management
- `GET /cv/` - CV listesi
- `POST /cv/create/` - Yeni CV oluşturma
- `GET /cv/{id}/` - CV detayları
- `POST /cv/{id}/edit/` - CV düzenleme

#### Job Analysis
- `GET /jobs/quick-apply/` - Hızlı başvuru sayfası
- `POST /jobs/quick-apply/` - İlan analizi
- `GET /jobs/history/` - Başvuru geçmişi

#### AI Settings
- `GET /ai/settings/` - AI ayarları
- `POST /ai/settings/` - AI ayarları güncelleme

### Response Formats
```json
{
  "match_score": 75,
  "decision": "REVIEW",
  "reasoning": "Strong IT experience but missing formal certification",
  "matched_skills": ["Python", "Django"],
  "missing_skills": ["Kubernetes", "AWS"]
}
```

---

## 🚀 Deployment

### Production Checklist
- [ ] `DEBUG=False`
- [ ] Güçlü `SECRET_KEY` ayarla
- [ ] `ALLOWED_HOSTS` yapılandır
- [ ] PostgreSQL kullan
- [ ] SSL/HTTPS etkinleştir
- [ ] Static files collect et
- [ ] Gunicorn + Nginx kullan

### Docker Deployment
```dockerfile
FROM python:3.13-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python manage.py collectstatic --noinput

EXPOSE 8000
CMD ["gunicorn", "py_JobAutomation.wsgi", "--bind", "0.0.0.0:8000"]
```

### Environment Variables (Production)
```bash
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgres://user:pass@host:5432/dbname
SECURE_SSL_REDIRECT=True
```

---

## 🔧 Troubleshooting

### Yaygın Sorunlar

#### ❌ "AI API Key Required"
**Sorun:** AI özellikler çalışmıyor
**Çözüm:**
1. `/ai/settings/` sayfasında API key girin
2. Sağlayıcı seçin (OpenAI/Gemini/Groq)
3. Kaydet ve sayfayı yenileyin

#### ❌ "NoReverseMatch" Hatası
**Sorun:** URL namespace eksik
**Çözüm:** Template'de `{% url 'app_name:view_name' %}` kullanın

#### ❌ "Permission Denied"
**Sorun:** Kullanıcı kendi verilerini göremiyor
**Çözüm:** Login olduğunuzdan emin olun

#### ❌ "AI Comparison Failed"
**Sorun:** AI çağrısı başarısız
**Çözüm:**
- API key'in doğru olduğunu kontrol edin
- Rate limit aşılmamış mı kontrol edin
- Ağ bağlantısını kontrol edin
- Sistem otomatik olarak heuristic fallback kullanacak

#### ❌ "Database Connection Error"
**Sorun:** Veritabanı bağlantısı yok
**Çözüm:**
```bash
python manage.py migrate
python manage.py dbshell  # DB bağlantısı test
```

### Debug Mode
```python
# settings.py
DEBUG = True
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'ai_bridge': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

### Test Çalıştırma
```bash
# Tüm testler
pytest

# Belirli app testi
pytest cv_manager/tests.py -v

# Coverage raporu
pytest --cov=. --cov-report=html
```

---

## 🔒 Güvenlik

### Best Practices
- ✅ **API Key Encryption**: Fernet symmetric encryption
- ✅ **User Isolation**: Her kullanıcı kendi verilerini görür
- ✅ **CSRF Protection**: Tüm formlar korunur
- ✅ **SQL Injection Prevention**: Django ORM kullanır
- ✅ **XSS Protection**: Template escaping aktif
- ✅ **Secure Headers**: Production'da HTTPS zorunlu

### API Key Güvenliği
- 🔐 Veritabanında **plain text** saklanmaz
- 🔐 **Fernet encryption** kullanılır
- 🔐 Her kullanıcı **kendi key'ini** yönetir
- 🔐 **Global key** fallback olarak kullanılır

### Session Security
```python
# settings.py
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
```

---

## 📊 Changelog

### Version 2.0 (Ocak 2026)
- ✨ **AI-Powered Job Matching**: Tam CV-iş karşılaştırması
- ✨ **User Authentication**: Kayıt/giriş sistemi
- ✨ **Fallback System**: AI başarısız olursa heuristic yedek
- ✨ **Dynamic CV Selection**: Akıllı alan seçimi
- ✨ **Multi-Provider AI**: OpenAI, Gemini, Groq desteği
- ✅ **62 Test Cases**: %68 coverage
- 🔒 **Security Enhancements**: API key encryption, user isolation

### Version 1.0 (Aralık 2025)
- 🎯 **İlk sürüm**: Temel CV yönetimi ve job analysis
- 🤖 **AI Integration**: OpenAI GPT-4o-mini desteği
- 📝 **Cover Letter Generation**: Almanca Anschreiben
- 🧪 **Testing Framework**: pytest entegrasyonu

---

## 🎯 Özellikler Roadmap

### Tamamlanan ✅
- ✅ Multi-provider AI desteği
- ✅ User authentication & isolation
- ✅ AI-powered CV-job matching
- ✅ Comprehensive test suite
- ✅ Template fallback sistemi
- ✅ API key encryption
- ✅ Production deployment hazır

### Gelecek Özellikler 🔄
- [ ] **PDF Export**: CV + Anschreiben PDF çıktısı
- [ ] **Email Automation**: Otomatik başvuru email'i
- [ ] **Job Tracking**: Başvuru durumu takibi
- [ ] **Multi-Language**: Türkçe, İngilizce desteği
- [ ] **Async Processing**: Celery ile AI işlemleri
- [ ] **Analytics Dashboard**: Kullanım istatistikleri
- [ ] **Mobile App**: React Native uygulaması
- [ ] **API Rate Limiting**: API kullanım kontrolü

---

## 🔧 Geliştirme

### Code Quality Tools
```bash
# Code formatting
black .

# Linting
flake8

# Import sorting
isort .
```

### Migration Oluşturma
```bash
python manage.py makemigrations
python manage.py migrate
```

### Static Files
```bash
python manage.py collectstatic
```

---

## 🤝 Katkıda Bulunma

Katkılarınızı bekliyoruz! Katkı yapmak için:

1. Bu projeyi **fork** edin
2. Yeni bir **branch** oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi **commit** edin (`git commit -m 'feat: Add amazing feature'`)
4. Branch'inizi **push** edin (`git push origin feature/amazing-feature`)
5. **Pull Request** açın

### Katkı Kuralları
- ✅ Testlerinizi ekleyin
- ✅ Code style kurallarına uyun (black, flake8)
- ✅ Commit mesajlarınızı anlamlı yazın
- ✅ Dokümantasyonu güncelleyin

---

## 📜 Lisans

Bu proje **MIT License** ile lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

---

## 📞 Destek & İletişim

### 🐛 Hata Bildirimi
Hata bulduysanız veya iyileştirme öneriniz varsa:

1. **GitHub Issues** açın: [New Issue](https://github.com/mhilmicicek07/py_JobAutomation/issues)
2. **Pull Request** gönderin: [Contribute](https://github.com/mhilmicicek07/py_JobAutomation/pulls)
3. **Discussions** bölümünden tartışın

### 📧 İletişim
- **Email**: mehmet@example.com
- **LinkedIn**: [Mehmet Hilmi Çiçek](https://linkedin.com/in/mehmet-hilmi-cicek)
- **GitHub**: [@mhilmicicek07](https://github.com/mhilmicicek07)

### ❓ SSS

**Q: AI API key zorunlu mu?**
A: Evet, temel özellikler (CV import, job analysis) için gereklidir.

**Q: Hangi AI sağlayıcıları destekleniyor?**
A: OpenAI (GPT-4o-mini), Google Gemini, Groq (Llama3).

**Q: Ücretsiz AI kredisi var mı?**
A: OpenAI $5, Gemini ücretsiz kota sağlar.

**Q: Production deployment için ne önerirsiniz?**
A: PostgreSQL + Gunicorn + Nginx + SSL.

**Q: Çoklu dil desteği gelecek mi?**
A: Planlanıyor: Türkçe, İngilizce desteği.

---

## 👨‍💻 Geliştirici

### Mehmet Hilmi Çiçek
**Full-Stack Developer & AI Enthusiast**

- 🎓 **Eğitim**: BWL (İşletme) + IT
- 💼 **Deneyim**: 3+ yıl IT Support, Flughafen Frankfurt
- 🛠️ **Skills**: Python, Django, React, AI/ML
- 🌟 **Uzmanlık**: AI-powered uygulamalar, web development

#### Projeler
- **[py_JobAutomation](https://github.com/mhilmicicek07/py_JobAutomation)** - AI-powered job application system
- **CV Management System** - Automated CV processing
- **AI Chat Applications** - Multiple AI provider integrations

---

## 🙏 Teşekkürler

Bu proje aşağıdaki teknolojiler ve topluluk sayesinde geliştirilmiştir:

### Core Technologies
- **Django Framework** - Robust web framework
- **Python 3.13** - Modern programming language
- **OpenAI API** - Advanced AI capabilities
- **Google Gemini** - Fast AI inference
- **Groq** - High-performance AI

### UI/UX
- **Bootstrap 5.3** - Responsive design
- **Font Awesome 6.x** - Beautiful icons
- **Django Templates** - Server-side rendering

### Development Tools
- **pytest** - Comprehensive testing
- **Black/Flake8** - Code quality
- **GitHub Actions** - CI/CD pipeline

### Community
- **Django Community** - Framework support
- **Open Source Contributors** - Libraries and tools
- **AI Research Community** - Latest advancements

---

## 📜 Lisans

Bu proje **MIT License** ile lisanslanmıştır.

```
MIT License - Özet:
✅ Ticari kullanım serbest
✅ Özel kullanım serbest
✅ Dağıtım serbest
✅ Değişiklik serbest
⚠️  Telif hakkı bildirimi zorunlu
```

Detaylar için: [LICENSE](LICENSE) dosyasına bakın.

---

## 🎯 Son Notlar

**py_JobAutomation** modern web teknolojileri ve yapay zeka kullanarak iş başvurusu sürecini otomatikleştiren, kullanıcı dostu ve güvenli bir uygulamadır.

### 🌟 Öne Çıkan Özellikler
- **AI-Powered Intelligence**: Gerçekçi job matching
- **Production-Ready**: Güvenlik ve performans odaklı
- **User-Centric**: Her kullanıcı kendi deneyimi
- **Extensible**: Yeni özellikler kolayca eklenebilir

### 🚀 Gelecek Vizyonu
- **Global Expansion**: Çoklu dil desteği
- **Advanced AI**: Daha akıllı matching algoritmaları
- **Mobile Apps**: iOS/Android uygulamaları
- **Enterprise Features**: Team collaboration, analytics

---

**Son Güncelleme**: Ocak 2026  
**Versiyon**: 2.0  
**Django**: 5.2.7  
**Python**: 3.13  
**Test Coverage**: 68%  
**License**: MIT
