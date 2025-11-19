# py_JobAutomation

Django tabanlı iş başvurusu otomasyonu (özel repo).

## Gereksinimler
- Python 3.13
- Django 5.2.7

## Kurulum
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

AI Entegrasyonu (OpenAI)
Bu proje isteğe bağlı olarak OpenAI kullanarak:


İlan metinlerinden gereksinim/skills çıkarabilir,


CV metinlerini (raw text) yapılandırılmış hale getirebilir (skills / experience / education),


Almanca Anschreiben (cover letter) üretebilir.


Mimari bilerek fallback’li tasarlandı:


OpenAI çalışmazsa veya kapatırsan:


Heuristik parser’lar ve template tabanlı Anschreiben devreye girer,


Uygulama “tamamen kör” kalmaz.




1. Gerekli Python paketi
requirements.txt zaten içeriyor:
pip install -r requirements.txt

Alternatif:
pip install openai

2. Ortam değişkeni (OPENAI_API_KEY)
OpenAI API anahtarını ortam değişkeni olarak vermen gerekiyor.
Örnek (PowerShell):
$env:OPENAI_API_KEY = "sk-...."
python manage.py runserver

Notlar:


Bu ayar sadece o terminal oturumu için geçerlidir.


Kalıcı yapmak istersen:


Windows “Environment Variables” (Kullanıcı değişkenleri) → OPENAI_API_KEY ekleyebilirsin.




API key’i asla repoya, koda, README’ye veya ekran görüntüsüne koyma.



Django Ayarları (settings.py)
py_JobAutomation/settings.py içinde AI ile ilgili bölüm:
AI_PROVIDER = "openai"   # "openai" veya "stub"

OPENAI_DEFAULT_MODEL = "gpt-4o-mini"

OPENAI_MODEL_CV = "gpt-4o-mini"         # CV extraction
OPENAI_MODEL_POSTING = "gpt-4o-mini"    # Job posting extraction
OPENAI_MODEL_LETTER = "gpt-4o-mini"     # Cover letter / Anschreiben

AI_COVER_LETTER_PROVIDER = "openai"     # "openai" veya "stub"

Tipik senaryolar:


OpenAI tamamen kapalı (sadece heuristik + template):
AI_PROVIDER = "stub"
AI_COVER_LETTER_PROVIDER = "stub"



OpenAI her yerde açık (şu anki varsayılan):
AI_PROVIDER = "openai"
AI_COVER_LETTER_PROVIDER = "openai"



Bu ayarlar değiştirilerek proje “offline / cheap mode” ile “full AI mode” arasında hızlıca alınabilir.

Nasıl Çalışıyor? (Kod Seviyesi)
1. İlan analizi (Job postings)
Fonksiyon:
from ai_bridge.services import ai_extract_posting



ai_extract_posting(posting):


posting.raw_text üzerinden çalışır.


AI_PROVIDER == "openai" ise OpenAI Responses API’yi JSON modda çağırır.


Herhangi bir hata durumunda (API key yok, limit, network vs.):


Hata logger.exception(...) ile loglanır,


job_analyzer.services.extract_requirements(...) heuristiğine otomatik düşer.




Dönen yapı:
{
    "skills": [...],
    "experience": [...],
    "target_field": posting.target_field,
}





Admin tarafında:


JobPosting modeli için actions:


AI: İlandan gereksinimleri çıkar (snapshot kaydet)


AI: Son ilan snapshot'ını uygula




Bu akış:


OpenAI / heuristik ile bir ExtractionSnapshot kaydediyor,


Son snapshot’ı JobPosting.extracted_skills, extracted_experience, match_score, decision alanlarına uyguluyor.




2. CV analizi (raw CV text → yapılandırılmış veri)
Fonksiyon:
from ai_bridge.services import ai_extract_cv



ai_extract_cv(cv_source):


cv_source.raw_text kullanan bir fonksiyon; model tipi önemli değil, raw_text alanı olsun yeter.


AI_PROVIDER == "openai" ise OpenAI CV parser’ı çalıştırır:


Çıktı şeması:
{
    "skills": [...],
    "experience": [
        {
            "title": "...",
            "company": "...",
            "start": "MM/YYYY" veya None,
            "end": "MM/YYYY" veya None,
            "description": "..."
        },
        ...
    ],
    "education": [
        {
            "degree": "...",
            "institution": "...",
            "start": "MM/YYYY" veya None,
            "end": "MM/YYYY" veya None,
            "status": "completed" | "ongoing" | "unknown"
        },
        ...
    ]
}





Hata durumunda:


Hata loglanır,


ai_extract_cv_text adlı heuristik parser’a düşer.






Admin actions (CV kaynağı için):


AI: CV’den çıkar (snapshot kaydet)


AI: Son CV snapshot'ını uygula


Bu akış:


ai_bridge.ExtractionSnapshot(kind="CV") kaydı oluşturur,


apply_cv_snapshot fonksiyonu ile:


cv_manager.Skill


cv_manager.Experience


cv_manager.Education
tablolarına merge ederek kayıt ekler (varsa tekrar etmiyor).




3. Anschreiben (Cover Letter) üretimi
Ana fonksiyon:
from applicant_letters.services import build_cover_letter

İmza:
build_cover_letter(cv, posting) -> str

Davranış:


AI_COVER_LETTER_PROVIDER == "openai" ise:


Önce _build_cover_letter_openai(...) çağrılır.


OpenAI tarafında bir hata olursa:


Hata logger.exception(...) ile loglanır,


Klasik template tabanlı Anschreiben’e otomatik düşer.






AI_COVER_LETTER_PROVIDER != "openai" ise:


Direkt template kullanılır.




Kullanılan veriler:


cv_sections = build_cv_sections(cv, posting) ile üretilen yapı:


profil


kenntnisse


erfahrung


ausbildung


hinweise


diagnostik (opsiyonel):
diagnostik = {
    "matched_skills": [...],  # hem CV’de hem ilanda geçen güçlü yanlar
    "missing_skills": [...]   # ilanda olup CV’de olmayanlar
}





AI tarafındaki önemli kurallar (prompt ile zorlanıyor):


Sadece JSON içindeki bilgilere dayanarak yazar,


“Bilmiyorum, eksiğim” tarzı negatif cümleler yazmamalı,


diagnostik.matched_skills → gerçek “Schwerpunkte”,


diagnostik.missing_skills → sadece “öğrenme hedefi / weiter ausbauen” şeklinde geçebilir, asla mevcut güç gibi lanse edilmez.


Fallback template:


AI çalışmasa bile:


“Meine Schwerpunkte liegen unter anderem in …” cümlesinde


Öncelikle diagnostik.matched_skills kullanılır,


missing_skills listeye hiç alınmaz,


Maksimum 6 skill gösterilir.






Admin tarafında:


JobPosting listesinde action:


Taslak oluştur (CV bölümleri + Anschreiben)




Bu action:


İlanın hedef alanına göre uygun CV’yi seçer,


build_cv_sections + build_cover_letter çağırır,


ApplicationDraft kaydı oluşturur/günceller:


cv_sections JSON


cover_letter metni


language = "de"







Logging
OpenAI ile ilgili hatalar şu modüllerde loglanır:


ai_bridge.services:


İlan parsing (ai_extract_posting)


CV parsing (ai_extract_cv)




applicant_letters.services:


AI tabanlı Anschreiben (build_cover_letter)




Geliştirme sırasında konsolda görebileceğin tipik log’lar:


OpenAI job posting extraction failed; falling back to heuristics.


OpenAI CV extraction failed; falling back to heuristics.


OpenAI cover letter generation failed; falling back to template.


Bu log’ları gördüğünde kontrol etmen gerekenler:


OPENAI_API_KEY gerçekten set mi?


Kullanılan model adları (OPENAI_MODEL_*) geçerli mi?


Gerekirse AI_PROVIDER ve AI_COVER_LETTER_PROVIDER geçici olarak "stub" yapılarak sistem saf heuristik + template modunda çalıştırılabilir.
