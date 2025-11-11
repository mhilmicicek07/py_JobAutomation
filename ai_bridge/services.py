from __future__ import annotations
from typing import Dict, Any, List, Tuple
from datetime import date
import re
from calendar import monthrange


# ── Yardımcılar ───────────────────────────────────────────────────────────────

def _parse_my(token: str) -> date | None:
    """
    'MM/YYYY' → date(Y, M, 1)
    Geçersizse None.
    """
    m = re.match(r"^\s*(\d{2})/(\d{4})\s*$", token)
    if not m:
        return None
    mm, yyyy = int(m.group(1)), int(m.group(2))
    if 1 <= mm <= 12:
        return date(yyyy, mm, 1)
    return None


def _split_lines(text: str) -> List[str]:
    return [ln.strip() for ln in (text or "").splitlines() if ln.strip()]


def _canonical_skill(s: str) -> str:
    s = (s or "").strip().lower()
    # küçük bir kanonik eşleme
    if s in {"rest", "api"}:
        return "rest api"
    if s in {"unit tests", "unittest"}:
        return "unit test"
    return s


def _uniq_keep_order(items: List[str]) -> List[str]:
    seen = set()
    out = []
    for it in items:
        k = it.lower()
        if k not in seen and k:
            seen.add(k)
            out.append(it)
    return out


# ── AI çıkarımı (POSTING) – zaten vardı, korunuyor ────────────────────────────

def ai_extract_posting(posting) -> Dict[str, Any]:
    """
    Şimdilik stub: job_analyzer.services.extract_requirements ile simüle ediyoruz.
    """
    from job_analyzer import services as ja_services
    data = ja_services.extract_requirements(posting.raw_text, posting.target_field)
    return {
        "skills": data.get("skills", []),
        "experience": data.get("experience", []),
        "target_field": posting.target_field,
    }


# ── AI çıkarımı (CV) – stub/heuristik ─────────────────────────────────────────

def ai_extract_cv_text(raw_text: str) -> Dict[str, Any]:
    """
    Heuristik: ham metinden skills, experience, education alanlarını çıkarır.
    Gerçek LLM entegrasyonu için aynı şemayı koru.
    output şeması:
    {
        "skills": ["python", "django", ...],
        "experience": [
            {
                "title": "...",
                "company": "...",
                "start": "MM/YYYY" | null,
                "end": "MM/YYYY" | null,
                "description": "..."
            }, ...
        ],
        "education": [
            {
                "degree": "...",
                "institution": "...",
                "start": "MM/YYYY" | null,
                "end": "MM/YYYY" | null,
                "status": "completed|ongoing|unknown"
            }, ...
        ]
    }
    """
    lines = _split_lines(raw_text)

    # Basit anahtar kelime sezgisi
    SKILL_TOKENS = [
        "python", "django", "rest api", "sql", "postgresql", "mysql", "sqlite",
        "javascript", "typescript", "react", "git", "docker", "linux",
        "sap", "sap fi", "f110", "ebics", "datev", "hgb", "excel",
    ]

    skills: List[str] = []
    for ln in lines:
        lower = ln.lower()
        for tok in SKILL_TOKENS:
            if tok in lower:
                skills.append(_canonical_skill(tok))
    skills = _uniq_keep_order(skills)

    # Deneyim yakalama: "MM/YYYY – MM/YYYY | Title | Company" veya "seit MM/YYYY | Title | Company"
    exp: List[Dict[str, Any]] = []
    exp_pattern = re.compile(
        r"(?:(seit)\s+(\d{2}/\d{4})|(\d{2}/\d{4})\s*[–-]\s*(\d{2}/\d{4}))\s*\|\s*([^|]+?)\s*\|\s*(.+)$",
        re.IGNORECASE,
    )
    descr_buffer: List[str] = []
    last_idx: int | None = None

    for idx, ln in enumerate(lines):
        m = exp_pattern.search(ln)
        if m:
            # önceki kaydın açıklamasını kapat
            if last_idx is not None and descr_buffer:
                exp[last_idx]["description"] = " ".join(descr_buffer).strip()
                descr_buffer = []

            seit_flag = bool(m.group(1))
            seit_my = m.group(2)
            start_my = m.group(3)
            end_my = m.group(4)
            title = m.group(5).strip()
            company = m.group(6).strip()

            start = _parse_my(seit_my or start_my) if (seit_my or start_my) else None
            end = None if seit_flag else _parse_my(end_my) if end_my else None

            exp.append({
                "title": title,
                "company": company,
                "start": (seit_my or start_my) or None,
                "end": None if seit_flag else (end_my or None),
                "description": "",
            })
            last_idx = len(exp) - 1
        else:
            # madde imi gibi satırları açıklama olarak ekle
            if last_idx is not None and (ln.startswith("•") or ln.startswith("-") or ln.startswith("*")):
                descr_buffer.append(ln.lstrip("•-* ").strip())

    if last_idx is not None and descr_buffer:
        exp[last_idx]["description"] = " ".join(descr_buffer).strip()

    # Eğitim yakalama: "MM/YYYY – MM/YYYY | Degree | Institution"
    edu: List[Dict[str, Any]] = []
    edu_pattern = re.compile(
        r"(\d{2}/\d{4})\s*[–-]\s*(\d{2}/\d{4})\s*\|\s*([^|]+?)\s*\|\s*(.+)$"
    )
    for ln in lines:
        m = edu_pattern.search(ln)
        if m:
            edu.append({
                "start": m.group(1),
                "end": m.group(2),
                "degree": m.group(3).strip(),
                "institution": m.group(4).strip(),
                "status": "completed",
            })

    return {"skills": skills, "experience": exp, "education": edu}


def ai_extract_cv(cv_source) -> Dict[str, Any]:
    """CVSource.raw_text üzerinden çıkarım."""
    return ai_extract_cv_text(cv_source.raw_text or "")


# ── Snapshot’ı CV tablolarına uygulama ─────────────────────────────────────────

def apply_cv_snapshot(cv, output: Dict[str, Any], merge: bool = True) -> Dict[str, int]:
    """
    Snapshot çıktısını CV’nin Education/Experience/Skill tablolarına uygular.
    merge=True: var olanı korur, yenileri ekler (basit eşleştirme).
    """
    from cv_manager.models import Skill, Experience, Education

    added_skills = 0
    added_exp = 0
    added_edu = 0

    # Skills
    curr_skills = set(Skill.objects.filter(cv=cv).values_list("name", flat=True))
    for name in output.get("skills", []) or []:
        cname = _canonical_skill(name)
        if merge and cname in {x.lower() for x in curr_skills}:
            continue
        Skill.objects.get_or_create(cv=cv, name=cname)
        added_skills += 1

    # Experience
    for e in output.get("experience", []) or []:
        start_d = _parse_my(e.get("start") or "") if e.get("start") else None
        end_d = _parse_my(e.get("end") or "") if e.get("end") else None
        title = (e.get("title") or "").strip()
        company = (e.get("company") or "").strip()
        desc = (e.get("description") or "").strip()

        if merge:
            exists = Experience.objects.filter(
                cv=cv, title=title, company=company, start_date=start_d or None, end_date=end_d or None
            ).exists()
            if exists:
                continue

        Experience.objects.create(
            cv=cv, title=title, company=company, start_date=start_d, end_date=end_d, description=desc
        )
        added_exp += 1

    # Education
    for ed in output.get("education", []) or []:
        start_d = _parse_my(ed.get("start") or "") if ed.get("start") else None
        end_d = _parse_my(ed.get("end") or "") if ed.get("end") else None
        degree = (ed.get("degree") or "").strip()
        inst = (ed.get("institution") or "").strip()

        if merge:
            exists = Education.objects.filter(
                cv=cv, degree=degree, institution=inst, start_date=start_d or None, end_date=end_d or None
            ).exists()
            if exists:
                continue

        Education.objects.create(
            cv=cv, degree=degree, institution=inst, start_date=start_d, end_date=end_d
        )
        added_edu += 1

    return {"skills": added_skills, "experience": added_exp, "education": added_edu}
