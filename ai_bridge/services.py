# ai_bridge/services.py
from __future__ import annotations
from typing import Dict, Any, List
from datetime import date
import re


# ── Yardımcılar ───────────────────────────────────────────────────────────────

def _split_lines(text: str) -> List[str]:
    """Boş satırları atarak satırlara böl."""
    return [ln.strip() for ln in (text or "").splitlines() if ln.strip()]


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


def _canonical_skill(s: str) -> str:
    """Eşanlamlıları kanonik hale getir."""
    s = (s or "").strip().lower()
    if s in {"rest", "api"}:
        return "rest api"
    if s in {"unit tests", "unittest"}:
        return "unit test"
    return s


def _uniq_keep_order(items: List[str]) -> List[str]:
    """Sıralı benzersizleştirme (case-insensitive)."""
    seen = set()
    out = []
    for it in items:
        k = it.lower()
        if k not in seen and k:
            seen.add(k)
            out.append(it)
    return out


# ── AI çıkarımı (POSTING) – stub/heuristik ────────────────────────────────────

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
    Gerçek LLM entegrasyonu için aynı şemayı korur.

    output:
    {
        "skills": ["python", "django", ...],
        "experience": [
            {"title": "...", "company": "...", "start": "MM/YYYY"|None, "end": "MM/YYYY"|None, "description": "..."},
            ...
        ],
        "education": [
            {"degree": "...", "institution": "...", "start": "MM/YYYY"|None, "end": "MM/YYYY"|None, "status": "completed|ongoing|unknown"},
            ...
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

    # ── Deneyim yakalama ──────────────────────────────────────────────────────
    # 1) Pipe'lı: "seit 01/2024 | Title | Company" veya "12/2023–01/2024 | Title | Company"
    exp_pattern_bar = re.compile(
        r"(?:(seit)\s+(\d{2}/\d{4})|(\d{2}/\d{4})\s*[–-]\s*(\d{2}/\d{4}|heute))\s*\|\s*([^|]+?)\s*\|\s*(.+)$",
        re.IGNORECASE,
    )
    # 2) Tireli: "Title – Company    12/2023–01/2024" veya "Title – Company    seit 01/2024"
    exp_pattern_dash = re.compile(
        r"^(?P<title>.+?)\s+[–-]\s+(?P<company>.+?)\s+(?:(?P<start>\d{2}/\d{4})\s*[–-]\s*(?P<end>\d{2}/\d{4}|heute)|seit\s+(?P<seit>\d{2}/\d{4}))$",
        re.IGNORECASE,
    )
    # 3) Virgüllü: "Title,    05/2022–10/2025" veya "Title,    seit 01/2024"
    exp_pattern_comma = re.compile(
        r"^(?P<title>.+?),\s+(?:(?P<start>\d{2}/\d{4})\s*[–-]\s*(?P<end>\d{2}/\d{4}|heute)|seit\s+(?P<seit>\d{2}/\d{4}))$",
        re.IGNORECASE,
    )

    exp: List[Dict[str, Any]] = []
    descr_buffer: List[str] = []
    last_idx: int | None = None

    for ln in lines:
        # Başlık satırı denemeleri
        m = exp_pattern_bar.search(ln)
        if m:
            seit_flag = bool(m.group(1))
            seit_my = m.group(2)
            start_my = m.group(3)
            end_my = m.group(4)
            title = m.group(5).strip()
            company = m.group(6).strip()
        else:
            m = exp_pattern_dash.search(ln)
            if m:
                seit_flag = bool(m.group("seit"))
                seit_my = m.group("seit")
                start_my = m.group("start")
                end_my = m.group("end")
                title = m.group("title").strip()
                company = m.group("company").strip()
            else:
                m = exp_pattern_comma.search(ln)
                if m:
                    seit_flag = bool(m.group("seit"))
                    seit_my = m.group("seit")
                    start_my = m.group("start")
                    end_my = m.group("end")
                    title = m.group("title").strip()
                    company = ""
                else:
                    # Bullet açıklama satırı yakala
                    if last_idx is not None:
                        if re.match(r"^[\u2022\u2219\u25CF\u00B7\u25E6\u2043\-\*•·●]", ln):
                            descr_buffer.append(re.sub(
                                r"^[\u2022\u2219\u25CF\u00B7\u25E6\u2043\-\*•·●\s]+", "", ln
                            ).strip())
                    continue  # başlık yoksa sıradaki satıra geç

        # Yeni başlık bulunduysa önceki kaydı kapat
        if last_idx is not None and descr_buffer:
            exp[last_idx]["description"] = " ".join(descr_buffer).strip()
            descr_buffer = []

        # Tarihleri dizge olarak sakla; parse edilmiş tarihler merge aşamasında kullanılacak
        end_is_heute = bool(end_my and str(end_my).lower() == "heute")
        exp.append({
            "title": title,
            "company": company,
            "start": (seit_my or start_my) or None,
            "end": None if (seit_flag or end_is_heute) else (end_my or None),
            "description": "",
        })
        last_idx = len(exp) - 1

    # Son kaydın açıklamasını kapat
    if last_idx is not None and descr_buffer:
        exp[last_idx]["description"] = " ".join(descr_buffer).strip()

    # ── Eğitim yakalama ───────────────────────────────────────────────────────
    edu: List[Dict[str, Any]] = []
    # 1) Pipe'lı: "MM/YYYY–MM/YYYY | Degree | Institution"
    edu_pattern_bar = re.compile(
        r"(\d{2}/\d{4})\s*[–-]\s*(\d{2}/\d{4})\s*\|\s*([^|]+?)\s*\|\s*(.+)$"
    )
    # 2) Tireli+virgüllü: "Degree – Institution, 08/2023–01/2024"
    edu_pattern_dash = re.compile(
        r"^(?P<degree>.+?)\s+[–-]\s+(?P<inst>.+?),\s*(?P<start>\d{2}/\d{4})\s*[–-]\s*(?P<end>\d{2}/\d{4})$"
    )
    # 3) Tam virgüllü: "Degree, Institution, 09/2011–08/2015"
    edu_pattern_deg_inst_comma = re.compile(
        r"^(?P<degree>.+?),\s*(?P<inst>.+?),\s*(?P<start>\d{2}/\d{4})\s*[–-]\s*(?P<end>\d{2}/\d{4})$"
    )
    # 4) Sadece derece + tarih: "Degree, 11/2017–12/2018"
    edu_pattern_comma = re.compile(
        r"^(?P<degree>.+?),\s*(?P<start>\d{2}/\d{4})\s*[–-]\s*(?P<end>\d{2}/\d{4})$"
    )
    # 5) Tek tarih: "Degree – Institution · 08/2023"
    edu_pattern_single = re.compile(
        r"^(?P<degree>.+?)\s+[–-]\s+(?P<inst>.+?)\s*[·,]\s*(?P<single>\d{2}/\d{4})$"
    )

    for ln in lines:
        m = edu_pattern_bar.search(ln)
        if m:
            edu.append({
                "start": m.group(1),
                "end": m.group(2),
                "degree": m.group(3).strip(),
                "institution": m.group(4).strip(),
                "status": "completed",
            })
            continue

        m = edu_pattern_dash.search(ln)
        if m:
            edu.append({
                "start": m.group("start"),
                "end": m.group("end"),
                "degree": m.group("degree").strip(),
                "institution": m.group("inst").strip(),
                "status": "completed",
            })
            continue

        m = edu_pattern_deg_inst_comma.search(ln)
        if m:
            edu.append({
                "start": m.group("start"),
                "end": m.group("end"),
                "degree": m.group("degree").strip(),
                "institution": m.group("inst").strip(),
                "status": "completed",
            })
            continue

        m = edu_pattern_comma.search(ln)
        if m:
            edu.append({
                "start": m.group("start"),
                "end": m.group("end"),
                "degree": m.group("degree").strip(),
                "institution": "",
                "status": "completed",
            })
            continue

        m = edu_pattern_single.search(ln)
        if m:
            edu.append({
                "start": m.group("single"),
                "end": None,
                "degree": m.group("degree").strip(),
                "institution": m.group("inst").strip(),
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
    curr_skill_names = list(Skill.objects.filter(cv=cv).values_list("name", flat=True))
    curr_skill_lower = {x.lower() for x in curr_skill_names}
    for name in (output.get("skills") or []):
        cname = _canonical_skill(name)
        if merge and cname in curr_skill_lower:
            continue
        Skill.objects.get_or_create(cv=cv, name=cname)
        added_skills += 1

    # Experience
    for e in (output.get("experience") or []):
        start_d = _parse_my(e.get("start") or "") if e.get("start") else None
        end_d = _parse_my(e.get("end") or "") if e.get("end") else None
        title = (e.get("title") or "").strip()
        company = (e.get("company") or "").strip()
        desc = (e.get("description") or "").strip()

        if merge:
            exists = False
            if title or company or start_d or end_d:
                exists = Experience.objects.filter(
                    cv=cv, title=title, company=company,
                    start_date=start_d or None, end_date=end_d or None
                ).exists()
            if exists:
                continue

        Experience.objects.create(
            cv=cv, title=title, company=company, start_date=start_d, end_date=end_d, description=desc
        )
        added_exp += 1

    # Education
    for ed in (output.get("education") or []):
        start_d = _parse_my(ed.get("start") or "") if ed.get("start") else None
        end_d = _parse_my(ed.get("end") or "") if ed.get("end") else None
        degree = (ed.get("degree") or "").strip()
        inst = (ed.get("institution") or "").strip()
        status = (ed.get("status") or "completed").strip()

        if merge:
            exists = False
            if degree or inst or start_d or end_d:
                exists = Education.objects.filter(
                    cv=cv, degree=degree, institution=inst,
                    start_date=start_d or None, end_date=end_d or None
                ).exists()
            if exists:
                continue

        Education.objects.create(
            cv=cv, degree=degree, institution=inst, start_date=start_d, end_date=end_d
        )
        added_edu += 1

    return {"skills": added_skills, "experience": added_exp, "education": added_edu}