# 🤖 py_JobAutomation

> **Django-basiertes System zur Automatisierung von Bewerbungsprozessen**  
> Yapay zeka destekli iş başvuru otomasyonu (Almanca Anschreiben üretimi, CV yönetimi, ilan analizi)

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2.7-green.svg)](https://www.djangoproject.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/Tests-56%20passed-brightgreen.svg)]()

---

## 📋 İçindekiler

- [Özellikler](#-özellikler)
- [Teknoloji Stack](#-teknoloji-stack)
- [Kurulum](#-kurulum)
- [AI Konfigürasyonu](#-ai-konfigürasyonu)
- [Kullanım](#-kullanım)
- [Testler](#-testler)
- [Proje Yapısı](#-proje-yapısı)
- [Katkıda Bulunma](#-katkıda-bulunma)

---

## ✨ Özellikler

### 📄 CV Yönetimi (`cv_manager`)
- ✅ Çoklu CV profili (Web Geliştirme, BWL, Genel)
- ✅ Detaylı CV Studio: Deneyim, Eğitim, Yetenekler, Diller (CEFR standartları)
- ✅ **AI ile CV İmport**: Ham metin → Yapılandırılmış veri (GPT-4o / Gemini / Groq)
- ✅ Kullanıcı bazlı veri izolasyonu
- ✅ Process tracking (Çalışma izni, istifa, ehliyet vs.)

### 🔍 İlan Analizi (`job_analyzer`)
- ✅ Otomatik beceri/deneyim çıkarımı (AI + heuristic fallback)
- ✅ CV-İlan eşleşme skoru (0-100)
- ✅ Akıllı karar verme: **APPLY** (≥80), **REVIEW** (≥50), **SKIP** (<50)
- ✅ Hızlı başvuru ekranı (tek tıkla analiz + Anschreiben)

### ✍️ Başvuru Mektubu (`applicant_letters`)
- ✅ **Almanca Anschreiben** üretimi (AI veya template)
- ✅ ATS uyumlu CV bölümleri (Profil, Kenntnisse, Erfahrung...)
- ✅ Diagnostik sistemi: Güçlü/eksik yetenekleri tespit eder
- ✅ Pozitif dil kullanımı (AI prompt'unda eksiklikleri negatif sunmaz)

### 🧠 AI Entegrasyonu (`ai_bridge`)
- ✅ **Multi-provider desteği**: OpenAI, Google Gemini, Groq
- ✅ **Kullanıcı bazlı API ayarları** (herkes kendi key'ini kullanır)
- ✅ **Otomatik API Key şifreleme** (Fernet encryption)
- ✅ Snapshot sistemi (AI çıktılarını kaydet/tekrar kullan)
- ✅ **Fallback mekanizması**: AI başarısız olursa heuristik parser devreye girer

---

## 🛠 Teknoloji Stack

| Kategori | Teknolojiler |
|----------|-------------|
| **Backend** | Django 5.2.7, Python 3.13 |
| **Database** | SQLite (dev), PostgreSQL (production) |
| **AI/ML** | OpenAI API, Google Gemini, Groq |
| **Frontend** | Bootstrap 5.3, Font Awesome |
| **Security** | Fernet Encryption, CSRF, User Auth |
| **Testing** | pytest, pytest-django |

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

## 🔐 AI Konfigürasyonu

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

### 1. CV Oluşturma

**Dashboard** → **Neuen CV anlegen**
- İsim, alan (Web/BWL/Genel), iletişim bilgileri girin
- **AI Import** ile ham CV metnini yapılandırılmış veriye çevirin

### 2. Hızlı Başvuru

**Schnellbewerbung** menüsünden:
1. İlan metnini yapıştırın
2. Hedef alanı seçin (Web/BWL/Genel)
3. **Analysieren** tıklayın
4. Sonuçlar:
   - 🎯 **Match Score**: CV-İlan uyum yüzdesi
   - 📊 **Skills Analizi**: Eşleşen ve eksik yetenekler
   - ✉️ **Anschreiben**: Hazır Almanca ön yazı
   - 📄 **CV Blöcke**: ATS uyumlu kopyala-yapıştır bölümleri

### 3. Geçmiş İşlemler

**Historie** menüsünden:
- Tüm başvuru taslakları
- Her bir başvurunun detayları
- Anschreiben'ları tekrar görüntüleme

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

## 🎯 Özellikler Roadmap

### Tamamlanan
- ✅ Multi-provider AI desteği
- ✅ API key encryption
- ✅ Comprehensive test suite
- ✅ Template fallback sistemi
- ✅ User-based settings

### Gelecek Özellikler
- [ ] PDF Export (CV + Anschreiben)
- [ ] Email otomasyonu
- [ ] İlan takip sistemi (başvuru durumu)
- [ ] Çoklu dil desteği (Türkçe, İngilizce)
- [ ] Celery ile async AI işlemleri
- [ ] Dashboard analytics

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

## 👨‍💻 Geliştirici

**Mehmet Hilmi Çiçek**

- GitHub: [@mhilmicicek07](https://github.com/mhilmicicek07)
- Repository: [py_JobAutomation](https://github.com/mhilmicicek07/py_JobAutomation)

---

## 📧 İletişim

Sorularınız, önerileriniz veya hata bildirimleri için:
- **GitHub Issues** kullanın
- **Pull Request** açabilirsiniz
- **Discussions** bölümünden tartışabilirsiniz

---

## 🙏 Teşekkürler

Bu proje aşağıdaki teknolojiler sayesinde geliştirilmiştir:
- Django Framework
- OpenAI API
- Google Gemini
- Groq
- Bootstrap
- Font Awesome

---

**Son Güncelleme**: Ocak 2026  
**Versiyon**: 2.0
