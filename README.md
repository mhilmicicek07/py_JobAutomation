# 🤖 py_JobAutomation

> **AI-Powered Job Application Automation System**  
> **Yapay Zeka Destekli İş Başvurusu Otomasyon Sistemi**  
> **KI-gestütztes Automatisierungssystem für Jobbewerbungen**

Canlı Sürüm / Live Demo / Live-Demo: [py-jobautomation.onrender.com](https://py-jobautomation.onrender.com)

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2.7-green.svg)](https://www.djangoproject.com/)
[![Tests](https://img.shields.io/badge/Tests-62%20passed-brightgreen.svg)]()
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🌍 Language Selection / Dil Seçimi / Sprachauswahl

- [🇹🇷 Türkçe](#-türkçe)
- [🇺🇸 English](#-english)
- [🇩🇪 Deutsch](#-deutsch)

---

## 🇹🇷 Türkçe

py_JobAutomation, iş arama sürecini otomatikleştirmek için geliştirilen yapay zeka destekli bir Django uygulamasıdır. CV’leri ve iş ilanlarını analiz eder, eşleştirir ve Almanca/İngilizce kapak mektupları üretir. Uygulama çoklu CV desteği, AI sağlayıcı seçimi ve fallback heuristikleri içerir.

### ✨ Özellikler
- 🤖 **AI Destekli Eşleştirme**: CV metni ve ilan metni AI veya heuristiklerle skorlanır, karar (APPLY/REVIEW/SKIP) üretilir.
- 📄 **CV Yönetimi**: Çoklu CV, alan (WEB/BWL/GEN) seçimi, ilişkili eğitim/deneyim/beceri/dil/sertifika süreçleri.
- ✍️ **Kapak Mektubu Üretimi**: Almanca ve İngilizce metin, CV bölümleri ve tanımlanan becerilerle oluşturulur.
- 🔐 **Kullanıcı & AI Ayarları**: Giriş/kayıt akışı, kullanıcıya özel AI sağlayıcı (OpenAI, Gemini, Groq) ve şifreli API anahtarı.
- 🛡️ **Fallback Heuristikleri**: AI başarısız olduğunda anahtar kelime tabanlı beceri çıkarımı ve skor hesaplama devreye girer.
- 🧭 **Geçmiş & Detay**: Başvuru geçmişi, oluşturulan taslaklar ve detay sayfaları.

### 🧱 Mimari
- Django uygulamaları: `users` (kimlik), `cv_manager` (CV CRUD), `job_analyzer` (ilan analizi + skor), `applicant_letters` (kapak mektubu), `ai_bridge` (sağlayıcı seçimi & şifreli anahtar).
- Şablonlar Bootstrap 5 ve Font Awesome ile `templates/base.html` üzerinden genişletilir.
- Ayarlar: `py_JobAutomation/settings.py` içerisinde AI eşiği, sağlayıcı seçimi, statik/medya dizinleri.

### 📦 Gereksinimler
- Python 3.13
- Django 5.2.7
- Varsayılan DB: SQLite (geliştirme)
- Opsiyonel: Docker & Docker Compose

### ⚙️ Ortam Değişkenleri (`.env`)
- `SECRET_KEY`: Django gizli anahtarı (geliştirmede varsayılan mevcut)
- `DEBUG`: `True/False`
- `ALLOWED_HOSTS`: Virgülle ayrılmış host listesi
- `AI_PROVIDER`: `openai|gemini|groq` (varsayılan `openai`)
- `AI_COVER_LETTER_PROVIDER`: Kapak mektubu için özel sağlayıcı (boşsa `AI_PROVIDER`)
- `OPENAI_*`, `GEMINI_*`, `GROQ_*`: Model adları (varsayılanlar settings’de tanımlı)
- `JOB_MATCH_THRESHOLD_APPLY` / `JOB_MATCH_THRESHOLD_REVIEW`: Skor eşikleri
- E-posta ayarları: `EMAIL_*`

### 🚀 Kurulum (Yerel)
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### 🐳 Docker
```bash
docker compose up -d --build
```

### 🔐 AI Sağlayıcı Ayarı
1) Giriş yapın → **Einstellungen** (AI Settings) sayfası  
2) Sağlayıcı seçin (OpenAI/Gemini/Groq), API anahtarını girin. Anahtar şifrelenmiş saklanır.  
3) Model adını boş bırakırsanız varsayılan kullanılır (ör. `gpt-4o-mini`, `gemini-1.5-flash`, `llama-3.3-70b-versatile`).

### 🧪 Testler
```bash
pytest
pytest --cov=. --cov-report=html
```

### 🧭 Kullanım Akışı
1) **CV Ekle**: `/cv/` üzerinden çoklu CV ve alan seçimi (WEB/BWL/GEN).  
2) **Hızlı Başvuru**: `/jobs/quick-apply/` ilan metnini yapıştırın, alan seçin.  
3) **Analiz**: Önce AI karşılaştırması denenir; başarısızsa heuristik beceri çıkarımı ve skor hesaplanır.  
4) **Kapak Mektubu**: AI ile oluşturulur, taslak kaydedilir.  
5) **Geçmiş**: `/jobs/history/` ile eski taslak ve detaylara bakın.

### ❓ Sorun Giderme
- AI uyarısı: API anahtarı yoksa sistem `StubProvider` kullanır ve boş sonuç döner.  
- Tek CV varsa alan seçimi gizlenir; çoklu CV’de alan eşleşmesi ve `is_primary` öncelikli kullanılır.  
- Statik dosyalar geliştirmede `static/`, üretimde `staticfiles/`.

---

## 🇺🇸 English

py_JobAutomation is a Django app that automates job applications. It analyzes resumes and job postings, matches them with AI or heuristics, and generates German/English cover letters. Multi-CV support, provider selection, and fallbacks are built in.

### ✨ Features
- 🤖 **AI Matching**: CV vs. posting comparison with scoring and APPLY/REVIEW/SKIP decision.
- 📄 **CV Management**: Multiple CVs with field tagging (WEB/BWL/GEN) plus education/experience/skill/language/certification processes.
- ✍️ **Cover Letters**: German and English letters built from CV sections and extracted skills.
- 🔐 **User & AI Settings**: Auth flows plus per-user AI provider (OpenAI, Gemini, Groq) with encrypted API key storage.
- 🛡️ **Fallback Heuristics**: Keyword extraction and scoring when AI fails or keys are missing.
- 🧭 **History & Details**: Application drafts saved with sections and cover letters.

### 🧱 Architecture
- Django apps: `users` (auth), `cv_manager` (CV CRUD), `job_analyzer` (analysis/scoring), `applicant_letters` (letters), `ai_bridge` (provider selection & encrypted keys).
- Templates extend `templates/base.html` with Bootstrap 5 + Font Awesome.
- Settings: thresholds, providers, static/media paths in `py_JobAutomation/settings.py`.

### 📦 Requirements
- Python 3.13, Django 5.2.7
- Default DB: SQLite (dev)
- Optional: Docker & Docker Compose

### ⚙️ Environment (`.env`)
- `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`
- `AI_PROVIDER`, `AI_COVER_LETTER_PROVIDER`
- Model names: `OPENAI_*`, `GEMINI_*`, `GROQ_*` (defaults set in settings)
- Thresholds: `JOB_MATCH_THRESHOLD_APPLY`, `JOB_MATCH_THRESHOLD_REVIEW`
- Email config: `EMAIL_*`

### 🚀 Local Setup
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### 🐳 Docker
```bash
docker compose up -d --build
```

### 🔐 AI Provider Setup
1) Sign in → go to **Einstellungen / AI Settings**  
2) Choose provider (OpenAI/Gemini/Groq), paste API key (stored encrypted).  
3) Leave model blank to use defaults (`gpt-4o-mini`, `gemini-1.5-flash`, `llama-3.3-70b-versatile`).

### 🧪 Tests
```bash
pytest
pytest --cov=. --cov-report=html
```

### 🧭 Usage Flow
1) **Add CV** at `/cv/` (field WEB/BWL/GEN).  
2) **Quick Apply** at `/jobs/quick-apply/`; paste posting text, pick field.  
3) **Analysis** runs AI first, falls back to heuristic extraction and scoring.  
4) **Cover Letter** generated and draft stored.  
5) **History** available at `/jobs/history/`.

### ❓ Troubleshooting
- No API key → `StubProvider` returns empty results; provide a key to enable AI.  
- Single CV hides field selector; multiple CVs honor `is_primary` then field fallback.  
- Static assets: `static/` in dev, `staticfiles/` in production.

---

## 🇩🇪 Deutsch

py_JobAutomation ist eine Django-App zur Automatisierung von Bewerbungen. Lebensläufe und Stellenanzeigen werden analysiert, gematcht und deutsche/englische Anschreiben generiert. Mehrere Lebensläufe, Provider-Auswahl und Fallbacks sind integriert.

### ✨ Funktionen
- 🤖 **KI-Matching**: CV vs. Anzeige mit Scoring und Entscheidung (APPLY/REVIEW/SKIP).
- 📄 **Lebenslauf-Verwaltung**: Mehrere CVs mit Feld-Tags (WEB/BWL/GEN) plus Bildung/Erfahrung/Skill/Sprache/Zertifizierung.
- ✍️ **Anschreiben**: Deutsche und englische Texte auf Basis der CV-Sektionen und extrahierter Skills.
- 🔐 **Benutzer & KI-Einstellungen**: Login/Registrierung, pro Benutzer AI-Provider (OpenAI, Gemini, Groq) mit verschlüsselten API-Keys.
- 🛡️ **Fallback-Heuristiken**: Schlüsselwort-Extraktion und Scoring, wenn KI fehlschlägt oder Schlüssel fehlt.
- 🧭 **Historie & Details**: Bewerbungsentwürfe werden gespeichert und können eingesehen werden.

### 🧱 Architektur
- Django-Apps: `users` (Auth), `cv_manager` (CV CRUD), `job_analyzer` (Analyse/Scoring), `applicant_letters` (Anschreiben), `ai_bridge` (Providerwahl & verschlüsselte Schlüssel).
- Templates basieren auf `templates/base.html` mit Bootstrap 5 + Font Awesome.
- Einstellungen: Schwellen, Provider, Static/Media in `py_JobAutomation/settings.py`.

### 📦 Anforderungen
- Python 3.13, Django 5.2.7
- Standard-DB: SQLite (Dev)
- Optional: Docker & Docker Compose

### ⚙️ Umgebungsvariablen (`.env`)
- `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`
- `AI_PROVIDER`, `AI_COVER_LETTER_PROVIDER`
- Modellnamen: `OPENAI_*`, `GEMINI_*`, `GROQ_*` (Defaults in Settings)
- Schwellen: `JOB_MATCH_THRESHOLD_APPLY`, `JOB_MATCH_THRESHOLD_REVIEW`
- E-Mail-Konfiguration: `EMAIL_*`

### 🚀 Lokales Setup
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### 🐳 Docker
```bash
docker compose up -d --build
```

### 🔐 KI-Provider einrichten
1) Anmelden → **Einstellungen / AI Settings** öffnen  
2) Provider wählen (OpenAI/Gemini/Groq), API-Key einfügen (verschlüsselt gespeichert).  
3) Modell leer lassen, um Defaults zu nutzen (`gpt-4o-mini`, `gemini-1.5-flash`, `llama-3.3-70b-versatile`).

### 🧪 Tests
```bash
pytest
pytest --cov=. --cov-report=html
```

### 🧭 Nutzungsablauf
1) **CV anlegen** unter `/cv/` (Feld WEB/BWL/GEN).  
2) **Quick Apply** unter `/jobs/quick-apply/`; Anzeigentext einfügen, Feld wählen.  
3) **Analyse**: zuerst KI, bei Fehler Heuristik-Extraktion + Scoring.  
4) **Anschreiben** wird erzeugt und als Entwurf gespeichert.  
5) **Historie** unter `/jobs/history/` einsehbar.

### ❓ Fehlerbehebung
- Kein API-Key → `StubProvider` liefert leere Ergebnisse; Schlüssel hinterlegen.  
- Nur ein CV blendet Feldauswahl aus; bei mehreren gilt `is_primary`, dann Feld-Fallback.  
- Statische Assets: `static/` in Dev, `staticfiles/` in Produktion.

---

## 📜 License / Lisans / Lizenz
MIT License (bkz. `LICENSE`).

## 👨‍💻 Developer
**Mehmet Hilmi Çiçek**  
- GitHub: [@mhilmicicek07](https://github.com/mhilmicicek07)  
- LinkedIn: [@mhilmicicek](https://linkedin.com/in/mhilmicicek)  
- Email: m.hilmicicek07@gmail.com
