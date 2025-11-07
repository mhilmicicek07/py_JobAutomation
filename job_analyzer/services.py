from __future__ import annotations
from typing import Dict, List, Set
from django.db.models import Q

# Basit anahtar kelime havuzu (MVP). Zamanla genişletiriz.
SKILL_KEYWORDS: Dict[str, Set[str]] = {
    "WEB": {
        "python", "django", "rest", "api", "rest api", "sql",
        "postgresql", "mysql", "javascript", "typescript", "react",
        "git", "docker", "ci/cd", "linux", "unit test", "unittest"
    },
    "BWL": {
        "sap", "sap fi", "sap f110", "f110", "ebics", "datev",
        "hgb", "ifrs", "monatsabschluss", "jahresabschluss",
        "kreditorenbuchhaltung", "debitorenbuchhaltung",
        "zahlungsverkehr", "controlling", "kostenrechnung",
        "excel", "ms excel", "kontoabstimmung"
    },
    "GEN": set(),
}

def _normalize_text(s: str) -> str:
    return (s or "").lower()

def extract_requirements(raw_text: str, target_field: str) -> Dict[str, List[str]]:
    """
    İlan metninden kaba beceri/deneyim çıkarımı (anahtar kelime eşleşmesi).
    """
    text = _normalize_text(raw_text)
    pool = SKILL_KEYWORDS.get(target_field, set()) | SKILL_KEYWORDS["GEN"]
    skills = sorted({kw for kw in pool if kw in text})
    # MVP: experience çıkarımını aynı havuzdan dönüyoruz; ileride ayrı set kullanırız.
    experience = skills.copy()
    return {"skills": skills, "experience": experience}

def get_primary_cv_or_fallback(field: str):
    """
    Önce is_primary=True ve eşleşen alan, sonra alan eşleşmesi, sonra GEN, en son herhangi biri.
    """
    from cv_manager.models import CV  # lazy import
    q = CV.objects

    # Öncelik sırası
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
    Basit skor: CV.skills isimleri ile ilan becerileri kesişimi / ilan becerileri.
    0–100 arası tamsayı.
    """
    if not cv or not skills_needed:
        return 0

    from cv_manager.models import Skill  # lazy import
    cv_skill_names = set(
        Skill.objects.filter(cv=cv).values_list("name", flat=True)
    )
    cv_skill_norm = {s.lower() for s in cv_skill_names}
    need_norm = {s.lower() for s in skills_needed}

    matched = cv_skill_norm & need_norm
    denom = len(need_norm) or 1
    pct = round(100 * len(matched) / denom)
    return max(0, min(100, pct))