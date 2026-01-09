from __future__ import annotations
from django.conf import settings
from typing import Iterable, Dict, List, Set
from django.db.models import Q
import re

# Basit anahtar kelime havuzu (MVP). Zamanla genişletiriz.
SKILL_KEYWORDS: Dict[str, Set[str]] = {
    "WEB": {
        "python", "django", "rest api", "rest", "api",
        "fastapi", "flask",
        "sql", "postgresql", "mysql", "sqlite",
        "javascript", "typescript", "react", "git",
        "docker", "linux", "unit test", "pytest", "ci cd",
    },
    "BWL": {
        "sap", "sap fi", "fi",
        "s4hana", "s/4hana", "sap s/4hana",
        "sap f110", "f110",
        "ebics", "datev",
        "hgb", "ifrs",
        "monatsabschluss", "jahresabschluss",
        "kreditorenbuchhaltung", "debitorenbuchhaltung",
        "zahlungsverkehr",
        "kontenabstimmung", "kontenklärung", "kontenpflege",
        "rechnungsprüfung", "kontierung", "rechnungseingang",
        "opos", "offene posten", "skonto",
        "mahnen", "mahnwesen",
        "excel", "pivottabellen", "sverweis", "power query",
    },
    "GEN": set(),
}

_CANON_MAP = {
    "rest": "rest api",
    "api": "rest api",
    "unit tests": "unit test",
    "unittest": "unit test",
    # CV-İş ilanı beceri eşleştirmesi
    "it support": "it-support",
    "unterstützung im it-support": "it-support",
    "it-support (tickets, benutzerverwaltung)": "it-support",
    "office organization": "büroorganisation",
    "administrative unterstützung und büroorganisation": "büroorganisation",
    "data management": "datenpflege",
    "datenpflege in digitalen systemen (dms/e-akte)": "datenpflege",
    "document control": "dokumentensteuerung",
    "bearbeitung von schriftverkehr und behördenkontakten": "schriftverkehr",
    "report creation": "berichterstellung",
    "ms office arbeiten": "ms-office",
    "windows applications": "ms-office",
    "basic accounting": "buchhaltung",
    "communication": "kommunikation",
    "flexibility": "flexibilität",
    "learning willingness": "lernbereitschaft",
    "teamwork": "teamarbeit",
    "user service": "benutzerservice",
    "programming (python, django, javascript, sql)": "programmierung",
    "web development": "webentwicklung",
    # Ek eşleştirmeler
    "administrative": "büroorganisation",
    "report creation": "berichterstellung",
    "document control": "dokumentensteuerung",
    "data management": "datenpflege",
    "user service": "benutzerservice",
    "flexibility": "flexibilität",
    "learning willingness": "lernbereitschaft",
    "communication": "kommunikation",
    "teamwork": "teamarbeit",
    # MS Office alt becerileri
    "word": "ms-office",
    "excel": "ms-office",
    "powerpoint": "ms-office",
    "outlook": "ms-office",
    "ms office": "ms-office",
    # Diğer beceriler
    "dms": "datenpflege",
    "e akte": "datenpflege",
    "benutzerverwaltung": "it-support",
    "digitale tools": "datenpflege",
}

def _canonicalize_skills(skills: Iterable[str]) -> List[str]:
    """Eşanlamlıları birleştir, gereksiz kopyaları at."""
    out: Set[str] = set()
    for s in skills:
        key = (s or "").strip().lower()
        key = _CANON_MAP.get(key, key)
        out.add(key)
    # 'rest api' varsa 'rest'/'api' zaten düşecek.
    return sorted(out)

def _normalize_text(s: str) -> str:
    s = (s or "").lower()
    s = s.replace("ß", "ss")
    s = re.sub(r"[\-_/]", " ", s)                 # tire/alt tire → boşluk
    s = re.sub(r"[.,;:(){}\[\]–—•·]", " ", s)     # noktalama temizle
    s = re.sub(r"\s+", " ", s).strip()            # boşlukları sadeleştir
    return s

def extract_requirements(raw_text: str, target_field: str) -> Dict[str, List[str]]:
    """
    İlan metninden akıllı beceri çıkarımı (anahtar kelime eşleşmesi + gruplama).
    """
    text = _normalize_text(raw_text)
    pool = SKILL_KEYWORDS.get(target_field, set()) | SKILL_KEYWORDS["GEN"]

    # Önce tüm becerileri çıkar
    found_skills = {kw for kw in pool if kw in text}

    # Becerileri gruplandır (üst beceri varsa alt becerileri çıkar)
    # MS Office grubu
    ms_office_keywords = {"word", "excel", "powerpoint", "outlook", "ms office"}
    if any(kw in found_skills for kw in ["ms office"] + list(ms_office_keywords)):
        # MS Office varsa alt becerileri kaldır, sadece "ms office" tut
        found_skills = (found_skills - ms_office_keywords) | {"ms office"}

    # Diğer gruplamalar eklenebilir (ileride)

    skills = sorted(found_skills)
    # MVP: experience çıkarımını aynı havuzdan dönüyoruz; ileride ayrı set kullanırız.
    experience = skills.copy()
    skills = _canonicalize_skills(skills)
    experience = _canonicalize_skills(experience)
    return {"skills": skills, "experience": experience}

def get_primary_cv_or_fallback(field: str, user=None):
    """
    Önce is_primary=True ve eşleşen alan, sonra alan eşleşmesi, sonra GEN, en son herhangi biri.
    Kullanıcıya göre filtreler. Eğer tek CV varsa direkt onu döndürür.
    """
    from cv_manager.models import CV  # lazy import
    
    # Kullanıcıya göre filtrele
    if user and user.is_authenticated:
        q = CV.objects.filter(user=user)
    else:
        q = CV.objects.all()
    
    # Eğer sadece 1 CV varsa direkt onu döndür (alan önemli değil)
    cv_count = q.count()
    if cv_count == 1:
        return q.first()
    
    if cv_count == 0:
        return None

    # Öncelik sırası (çoklu CV varsa)
    obj = q.filter(field=field, is_primary=True).first()
    if obj:
        return obj

    obj = q.filter(field=field).first()
    if obj:
        return obj

    obj = q.filter(field="GEN").first()
    if obj:
        return obj

    return q.first()

def score_posting_against_cv(cv, skills_needed: List[str]) -> int:
    """
    Akıllı skor: CV.skills isimleri ile ilan becerileri canonical eşleşmesi / ilan becerileri.
    0–100 arası tamsayı.
    """
    if not cv or not skills_needed:
        return 0

    from cv_manager.models import Skill  # lazy import
    cv_skill_names = set(
        Skill.objects.filter(cv=cv).values_list("name", flat=True)
    )

    print(f"DEBUG: CV skills: {cv_skill_names}")
    print(f"DEBUG: Job skills needed: {skills_needed}")

    # Canonical eşleştirme uygula
    cv_skill_canon = {_canonicalize_skill_name(s) for s in cv_skill_names}
    need_canon = {_canonicalize_skill_name(s) for s in skills_needed}

    print(f"DEBUG: CV canonical skills: {cv_skill_canon}")
    print(f"DEBUG: Job canonical skills: {need_canon}")

    matched = cv_skill_canon & need_canon
    print(f"DEBUG: Matched canonical skills: {matched}")

    denom = len(need_canon) or 1
    pct = round(100 * len(matched) / denom)
    print(f"DEBUG: Score calculation: {len(matched)} / {denom} = {pct}%")

    return max(0, min(100, pct))

def _canonicalize_skill_name(skill_name: str) -> str:
    """
    Becerileri canonical forma dönüştür (Almanca/İngilizce eşleştirmesi).
    """
    if not skill_name:
        return ""

    # Küçük harfe çevir ve normalize et
    normalized = _normalize_text(skill_name)

    # Canonical map'ten eşleşme bul
    return _CANON_MAP.get(normalized, normalized)

def decision_from_score(score: int | None) -> str:
    apply_t = getattr(settings, "JOB_MATCH_THRESHOLDS", {}).get("APPLY", 80)
    review_t = getattr(settings, "JOB_MATCH_THRESHOLDS", {}).get("REVIEW", 50)
    if score is None:
        return "REVIEW"
    if score >= apply_t:
        return "APPLY"
    if score >= review_t:
        return "REVIEW"
    return "SKIP"