# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-01-08

### Added
- ✨ **Gemini AI Provider**: Google Gemini entegrasyonu eklendi
- ✨ **Groq AI Provider**: Groq (Llama3, Mixtral) desteği eklendi
- 🔐 **API Key Encryption**: Fernet encryption ile otomatik şifreleme
- 🧪 **Comprehensive Test Suite**: 50+ test case eklendi
  - cv_manager tests
  - job_analyzer tests
  - ai_bridge tests
  - applicant_letters tests
- 📋 **Requirements.txt**: Tüm bağımlılıklar dokümante edildi
- 🚫 **.gitignore**: Gereksiz dosyalar git'ten çıkarıldı
- 🔧 **env.example**: Environment variables template'i
- 📊 **pytest Configuration**: pytest.ini ve .coveragerc
- 📚 **CHANGELOG.md**: Bu dosya
- 🎨 **Enhanced Admin Panel**: 
  - Renkli badge'ler
  - Preview fonksiyonları
  - AI + Heuristic action seçenekleri
  - Date hierarchy
  - Search improvements

### Changed
- 📖 **README.md**: Tamamen yeniden yazıldı
  - Detaylı kurulum talimatları
  - AI provider konfigürasyonu
  - Test çalıştırma örnekleri
  - Proje yapısı açıklaması
  - Roadmap eklendi
- 🔄 **UserAISettings Model**: API key field 512 karaktere çıkarıldı
- 🎯 **Provider System**: get_provider() artık otomatik decrypt ediyor

### Fixed
- 🐛 AI provider seçimi için fallback mekanizması iyileştirildi
- 🐛 Template'lerde eksik olan değişkenler düzeltildi

### Security
- 🔒 API key'ler artık encrypt edilerek saklanıyor
- 🔒 Plain text API key'ler otomatik migrate edilecek

---

## [1.0.0] - 2025-12-XX

### Added
- 🎉 İlk versiyon
- CV yönetim sistemi
- İş ilanı analizi
- OpenAI entegrasyonu
- Anschreiben üretimi
- Template fallback sistemi

---

## Gelecek Versiyonlar

### [2.1.0] - Planlanan
- [ ] PDF Export özelliği
- [ ] Email otomasyonu
- [ ] Celery async işlemler
- [ ] Dashboard analytics

### [2.2.0] - Planlanan
- [ ] Çoklu dil desteği (TR, EN)
- [ ] İlan takip sistemi
- [ ] Browser extension
