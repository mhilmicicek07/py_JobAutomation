# 🚀 Upgrade Notes - Version 2.0.0

## Önemli Değişiklikler

### 1. API Key Encryption (ÖNEMLİ!)

**Ne Değişti:**
- `UserAISettings.api_key` alanı artık otomatik şifreleniyor
- Veritabanında plain text yerine Fernet encryption kullanılıyor

**Yapmanız Gerekenler:**
```bash
# 1. Migration çalıştırın
python manage.py makemigrations ai_bridge
python manage.py migrate

# 2. Mevcut API key'ler otomatik migrate edilecek
# (İlk save edildiğinde şifrelenecek)
```

**Not:** Django SECRET_KEY değişirse, mevcut API key'ler çözülemez! SECRET_KEY'i **asla değiştirmeyin** production'da.

---

### 2. Yeni Bağımlılıklar

```bash
pip install -r requirements.txt
```

**Yeni paketler:**
- `google-generativeai` - Gemini AI desteği
- `groq` - Groq AI desteği  
- `cryptography` - API key şifreleme
- `python-decouple` - Environment variables
- `pytest`, `pytest-django`, `pytest-cov` - Testing

---

### 3. AI Provider Konfigürasyonu

**Önceden:**
```python
# settings.py
AI_PROVIDER = "openai"
```

**Şimdi:**
Kullanıcı bazlı ayarlar! Her kullanıcı `/ai/settings/` sayfasından kendi provider'ını seçebilir:
- OpenAI (GPT-4o-mini)
- Google Gemini
- Groq (Llama3, Mixtral)

---

### 4. Admin Panel İyileştirmeleri

**Yeni Action'lar:**
- 🔍 İlanı AI ile analiz et
- 📝 İlanı heuristik ile analiz et (AI olmadan)
- ✍️ Taslak oluştur

**Yeni Görünüm:**
- Renkli badge'ler (APPLY=yeşil, REVIEW=turuncu, SKIP=kırmızı)
- Preview alanları
- Date hierarchy
- Geliştirilmiş arama

---

### 5. Test Suite

**Yeni testler:**
```bash
# Tüm testleri çalıştır
pytest

# Coverage raporu
pytest --cov=. --cov-report=html
```

50+ test case eklendi:
- Model testleri
- View testleri
- Servis testleri
- Provider testleri

---

## Migration Checklist

- [ ] `pip install -r requirements.txt`
- [ ] `python manage.py makemigrations`
- [ ] `python manage.py migrate`
- [ ] `.env` dosyası oluştur (`env.example` kullan)
- [ ] Kullanıcı ayarlarından AI provider yapılandır
- [ ] Testleri çalıştır: `pytest`
- [ ] Admin paneli kontrol et

---

## Rollback

Eğer v1.0'a geri dönmek isterseniz:

```bash
git checkout v1.0.0
pip install -r requirements.txt
python manage.py migrate
```

**Uyarı:** API key'ler şifrelendiği için rollback sonrası tekrar girilmeli!

---

## Destek

Sorun yaşarsanız:
1. GitHub Issues açın
2. Loglara bakın: `python manage.py runserver` çıktısı
3. Test sonuçlarını kontrol edin: `pytest -v`

---

**Son Güncelleme:** 08 Ocak 2026
