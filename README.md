# 🤖 py_JobAutomation

> **AI-Powered Job Application Automation System**  
> **Yapay Zeka Destekli İş Başvurusu Otomasyon Sistemi**  
> **KI-gestütztes Automatisierungssystem für Jobbewerbungen**

Canlı Sürüm / Live Demo: [py-jobautomation.onrender.com](https://py-jobautomation.onrender.com)

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

Bu proje, iş arama sürecini kolaylaştırmak için geliştirilmiş, yapay zeka destekli bir otomasyon sistemidir. Adayların özgeçmişlerini analiz eder, iş ilanları ile eşleştirir ve profesyonel kapak mektupları hazırlar.

### ✨ Özellikler
- 🤖 **AI Destekli İş Eşleştirme**: CV ve iş ilanı arasında bağlamsal analiz ve puanlama.
- 📄 **Özgeçmiş Yönetimi**: Çoklu profil desteği ve AI ile veri içe aktarma.
- ✍️ **Otomatik Kapak Mektubu**: Almanca "Anschreiben" ve İngilizce "Cover Letter" üretimi.
- 🔐 **Kullanıcı Yönetimi**: Güvenli kayıt ve giriş sistemi.
- 🛡️ **Yedekleme Sistemi**: AI servisleri ulaşılamaz olduğunda dahi çalışma yeteneği.
- 📊 **Başvuru Geçmişi**: Tüm başvuru süreçlerini takip edebilme.

### 🔧 Son Güncellemeler
- Hızlı Başvuru (Quick Apply) artık kayıtlı CV yoksa veya seçilen alanla eşleşen bir CV bulunamazsa kullanıcıyı bilgilendirir ve işlem yapmaz.
- AI ile içe aktarılan deneyimlerin başlangıç tarihi artık opsiyoneldir; tarih gönderilmemiş olsa bile kayıt tamamlanır.
- Eğitim durumu alanı, modelde tanımlı `completed/ongoing` seçenekleriyle uyumlu olacak şekilde otomatik normalize edilir.

### 🛠️ Teknoloji Yığını
- **Backend**: Django 5.2.7, Python 3.13
- **AI**: OpenAI, Google Gemini, Groq
- **Veritabanı**: SQLite (Geliştirme için)
- **Frontend**: Bootstrap 5, Font Awesome
- **Test**: pytest, coverage

---

## 🇺🇸 English

This project is an AI-powered automation system designed to streamline the job search process. It analyzes candidates' resumes, matches them with job postings, and prepares professional cover letters.

### ✨ Features
- 🤖 **AI-Powered Job Matching**: Smart CV-job analysis with contextual scoring.
- 📄 **CV Management**: Multi-profile CV system with AI import capabilities.
- ✍️ **Automated Cover Letters**: Generation of German "Anschreiben" and English cover letters.
- 🔐 **User Authentication**: Secure login and registration system.
- 🛡️ **Fallback System**: Reliable operation even when AI providers are unavailable.
- 📊 **Application History**: Track and manage all your job applications in one place.

### 🛠️ Tech Stack
- **Backend**: Django 5.2.7, Python 3.13
- **AI**: OpenAI, Google Gemini, Groq
- **Database**: SQLite
- **Frontend**: Bootstrap 5, Font Awesome
- **Testing**: pytest, coverage

---

## 🇩🇪 Deutsch

Dieses Projekt ist ein KI-gestütztes Automatisierungssystem, das den Prozess der Jobsuche optimiert. Es analysiert die Lebensläufe der Kandidaten, vergleicht sie mit Stellenanzeigen und erstellt professionelle Anschreiben.

### ✨ Funktionen
- 🤖 **KI-gestütztes Job-Matching**: Intelligente Analyse von Lebenslauf und Stellenanzeige mit kontextbezogener Bewertung.
- 📄 **Lebenslauf-Verwaltung**: System für mehrere Profile mit KI-basiertem Datenimport.
- ✍️ **Automatische Anschreiben**: Erstellung von professionellen deutschen Anschreiben und englischen Cover Letters.
- 🔐 **Benutzerauthentifizierung**: Sicheres Registrierungs- und Anmeldesystem.
- 🛡️ **Fallback-System**: Funktioniert auch dann zuverlässig, wenn KI-Dienste nicht verfügbar sind.
- 📊 **Bewerbungshistorie**: Behalten Sie den Überblick über alle Ihre Bewerbungen.

---

## 🚀 Quick Start / Hızlı Başlangıç / Schnellstart

### 1. Clone & Setup
```bash
git clone https://github.com/mhilmicicek07/py_JobAutomation.git
cd py_JobAutomation
```

### 2. Local Setup (Venv)
```bash
python -m venv venv
# Windows: venv\Scripts\activate | Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
cp env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### 3. Docker (Recommended)
```bash
docker compose up -d --build
```

---

## 🧪 Testing / Testler
```bash
pytest
pytest --cov=. --cov-report=html
```

---

## 📜 License
This project is licensed under the **MIT License**.

## 👨‍💻 Developer
**Mehmet Hilmi Çiçek**
- GitHub: [@mhilmicicek07](https://github.com/mhilmicicek07)
- LinkedIn: [@mhilmicicek](https://linkedin.com/in/mhilmicicek)
- Email: m.hilmicicek07@gmail.com
