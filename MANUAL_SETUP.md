# 🛠️ Manuel Kurulum ve Commit Rehberi

## PowerShell Sorunu Çözümü

Eğer PowerShell ile sorun yaşıyorsanız, aşağıdaki adımları **Command Prompt (cmd)** ile takip edin:

---

## Adım 1: Migration Oluştur

```cmd
cd "G:\Drive'ım\GITHUB REPOS\py_JobAutomation"
python manage.py makemigrations ai_bridge
python manage.py migrate
```

**Beklenen Çıktı:**
```
Migrations for 'ai_bridge':
  ai_bridge\migrations\0004_alter_useraisettings_api_key.py
    - Alter field api_key on useraisettings
```

---

## Adım 2: Git Commit

### 2a. Tüm Değişiklikleri Ekle

```cmd
git add .
```

### 2b. Durumu Kontrol Et

```cmd
git status
```

**Göreceğiniz dosyalar:**
```
new file:   requirements.txt
new file:   .gitignore
new file:   env.example
new file:   pytest.ini
new file:   .coveragerc
new file:   CHANGELOG.md
new file:   UPGRADE_NOTES.md
new file:   IMPROVEMENTS_SUMMARY.md
new file:   MANUAL_SETUP.md
new file:   commit_changes.bat
new file:   ai_bridge/encryption.py
modified:   README.md
modified:   ai_bridge/models.py
modified:   ai_bridge/providers.py
modified:   job_analyzer/admin.py
modified:   applicant_letters/admin.py
modified:   cv_manager/tests.py
modified:   job_analyzer/tests.py
modified:   ai_bridge/tests.py
modified:   applicant_letters/tests.py
```

### 2c. Commit Yap

```cmd
git commit -m "feat: Major upgrade to v2.0.0 - Multi-provider AI, encryption, comprehensive tests"
```

veya detaylı commit için `commit_changes.bat` scriptini çalıştırın:

```cmd
commit_changes.bat
```

---

## Adım 3: GitHub'a Push

```cmd
git push origin main
```

veya farklı branch kullanıyorsanız:

```cmd
git push origin master
```

---

## Adım 4: Testleri Çalıştır

```cmd
pip install -r requirements.txt
pytest
```

**Beklenen Sonuç:**
```
============================= test session starts =============================
collected 55+ items

cv_manager/tests.py ..................... [ 38%]
job_analyzer/tests.py .............. [ 65%]
ai_bridge/tests.py ......... [ 82%]
applicant_letters/tests.py ......... [100%]

======================== 55 passed in 3.45s ========================
```

---

## Adım 5: Sunucuyu Başlat

```cmd
python manage.py runserver
```

Tarayıcıda `http://127.0.0.1:8000` adresine gidin.

---

## Sorun Giderme

### Problem: Migration hatası

**Çözüm:**
```cmd
python manage.py makemigrations
python manage.py migrate --run-syncdb
```

### Problem: Import hatası (cryptography modülü)

**Çözüm:**
```cmd
pip install cryptography
```

### Problem: Test hatası

**Çözüm:**
```cmd
pip install pytest pytest-django pytest-cov
pytest -v
```

### Problem: Git push redded

**Çözüm:**
```cmd
git pull origin main --rebase
git push origin main
```

---

## Hızlı Başlangıç (Tek Komut)

Windows Command Prompt'ta:

```cmd
cd "G:\Drive'ım\GITHUB REPOS\py_JobAutomation" && pip install -r requirements.txt && python manage.py makemigrations && python manage.py migrate && pytest && git add . && git commit -m "feat: v2.0.0 upgrade" && git push origin main
```

---

## Kontrol Listesi

- [ ] Migration oluşturuldu ve çalıştırıldı
- [ ] requirements.txt yüklendi
- [ ] Testler çalıştırıldı ve geçti
- [ ] Git commit yapıldı
- [ ] GitHub'a push edildi
- [ ] Sunucu çalışıyor
- [ ] `/ai/settings/` sayfası erişilebilir
- [ ] Admin paneli düzgün görünüyor

---

**Not:** Tüm komutları **Command Prompt (cmd)** veya **Git Bash** ile çalıştırın, PowerShell sorunlu olabilir.
