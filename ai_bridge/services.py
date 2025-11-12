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


# ── AI çıkarımı (CV) – bölüm farkında stub/heuristik ─────────────────────────

def ai_extract_cv_text(raw_text: str) -> Dict[str, Any]:
    """
    Ham metinden skills, experience, education alanlarını çıkarır.
    Çıktı şeması:
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

    # Basit anahtar kelime sezgisi (WEB + biraz BWL)
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

    # ── Desenler ───────────────────────────────────────────────────────────────
    # Experience başlıkları
    exp_pattern_bar = re.compile(
        r"(?:(seit)\s+(\d{2}/\d{4})|(\d{2}/\d{4})\s*[–-]\s*(\d{2}/\d{4}|heute))\s*\|\s*([^|]+?)\s*\|\s*(.+)$",
        re.IGNORECASE,
    )
    exp_pattern_dash = re.compile(
        r"^(?P<title>.+?)\s+[–-]\s+(?P<company>.+?)\s+(?:(?P<start>\d{2}/\d{4})\s*[–-]\s*(?P<end>\d{2}/\d{4}|heute)|seit\s+(?P<seit>\d{2}/\d{4}))$",
        re.IGNORECASE,
    )
    exp_pattern_comma = re.compile(
        r"^(?P<title>.+?),\s+(?:(?P<start>\d{2}/\d{4})\s*[–-]\s*(?P<end>\d{2}/\d{4}|heute)|seit\s+(?P<seit>\d{2}/\d{4}))$",
        re.IGNORECASE,
    )

    # Education başlıkları
    edu_pattern_bar = re.compile(
        r"(\d{2}/\d{4})\s*[–-]\s*(\d{2}/\d{4})\s*\|\s*([^|]+?)\s*\|\s*(.+)$"
    )
    edu_pattern_dash = re.compile(
        r"^(?P<degree>.+?)\s+[–-]\s+(?P<inst>.+?),\s*(?P<start>\d{2}/\d{4})\s*[–-]\s*(?P<end>\d{2}/\d{4})$"
    )
    edu_pattern_deg_inst_comma = re.compile(
        r"^(?P<degree>.+?),\s*(?P<inst>.+?),\s*(?P<start>\d{2}/\d{4})\s*[–-]\s*(?P<end>\d{2}/\d{4})$"
    )
    edu_pattern_comma = re.compile(
        r"^(?P<degree>.+?),\s*(?P<start>\d{2}/\d{4})\s*[–-]\s*(?P<end>\d{2}/\d{4})$"
    )
    edu_pattern_single = re.compile(
        r"^(?P<degree>.+?)\s+[–-]\s+(?P<inst>.+?)\s*[·,]\s*(?P<single>\d{2}/\d{4})$"
    )
    # İki satırlı eğitim biçimi
    edu_pattern_header_pending = re.compile(
        r"^(?P<degree>.+?)\s+[–-]\s+(?P<inst>.+?),\s*$"
    )
    edu_pattern_dates_only = re.compile(
        r"^\s*(?P<start>\d{2}/\d{4})\s*[–-]\s*(?P<end>\d{2}/\d{4})\s*$"
    )

    # ── Çıktı biriktiriciler ──────────────────────────────────────────────────
    exp: List[Dict[str, Any]] = []
    edu: List[Dict[str, Any]] = []
    descr_buffer: List[str] = []
    last_idx: int | None = None

    # Bölüm durumu
    sec = None            # None | "exp" | "edu"
    pending_edu = None    # (degree, inst) iki satırlı eğitim için bekletme

    # Bullet karakterleri
    BULLET_RE = r"^[\u2022\u2219\u25CF\u00B7\u25E6\u2043\-\*•·●]"

    for ln in lines:
        low = ln.lower().strip()

        # Bölüm başlıklarını yakala
        if re.match(r"^berufserfahrungen\b", low):
            if last_idx is not None and descr_buffer:
                exp[last_idx]["description"] = " ".join(descr_buffer).strip()
                descr_buffer = []
                last_idx = None
            sec = "exp"
            pending_edu = None
            continue

        if re.match(r"^ausbildung\b", low) or re.match(r"^ausbildung\s*&\s*weiterbildung\b", low) or re.match(r"^weiterbildung\b", low):
            if last_idx is not None and descr_buffer:
                exp[last_idx]["description"] = " ".join(descr_buffer).strip()
                descr_buffer = []
                last_idx = None
            sec = "edu"
            pending_edu = None
            continue

        if re.match(r"^kenntnisse\b", low) or re.match(r"^skills\b", low) or re.match(r"^fremdsprachen\b", low) or re.match(r"^über mich\b", low):
            # Açık exp açıklamasını kapat
            if last_idx is not None and descr_buffer:
                exp[last_idx]["description"] = " ".join(descr_buffer).strip()
                descr_buffer = []
                last_idx = None
            sec = None
            pending_edu = None
            continue

        # ----- Experience başlıkları (yalnızca exp bölümünde veya bölüm belirtilmemişse) -----
        matched_header = False
        if sec in (None, "exp"):
            m = exp_pattern_bar.search(ln)
            if m:
                matched_header = True
                seit_flag = bool(m.group(1))
                seit_my = m.group(2)
                start_my = m.group(3)
                end_my = m.group(4)
                title = m.group(5).strip()
                company = m.group(6).strip()
            else:
                m = exp_pattern_dash.search(ln)
                if m:
                    matched_header = True
                    seit_flag = bool(m.group("seit"))
                    seit_my = m.group("seit")
                    start_my = m.group("start")
                    end_my = m.group("end")
                    title = m.group("title").strip()
                    company = m.group("company").strip()
                else:
                    m = exp_pattern_comma.search(ln)
                    if m:
                        matched_header = True
                        seit_flag = bool(m.group("seit"))
                        seit_my = m.group("seit")
                        start_my = m.group("start")
                        end_my = m.group("end")
                        title = m.group("title").strip()
                        company = ""

        if matched_header:
            # önceki exp kaydının açıklamasını kapat
            if last_idx is not None and descr_buffer:
                exp[last_idx]["description"] = " ".join(descr_buffer).strip()
                descr_buffer = []

            # baştaki bullet karakterlerini başlıktan temizle
            title = re.sub(rf"{BULLET_RE}\s*", "", title)

            end_is_heute = bool(end_my and str(end_my).lower() == "heute")
            exp.append({
                "title": title,
                "company": company,
                "start": (seit_my or start_my) or None,
                "end": None if (seit_flag or end_is_heute) else (end_my or None),
                "description": "",
            })
            last_idx = len(exp) - 1
            continue

        # Başlık değilse ve exp bölümündeysek: bullet açıklamaları
        if sec in (None, "exp") and last_idx is not None:
            if re.match(BULLET_RE, ln):
                descr_buffer.append(re.sub(rf"{BULLET_RE}\s*", "", ln).strip())
                continue

        # ----- Education (yalnızca edu bölümünde) -----
        if sec == "edu":
            # İki satırlı: önce header, sonra sadece tarih
            m = edu_pattern_header_pending.search(ln)
            if m:
                degree = re.sub(rf"{BULLET_RE}\s*", "", m.group("degree").strip())
                inst = re.sub(rf"{BULLET_RE}\s*", "", m.group("inst").strip())
                pending_edu = (degree, inst)
                continue

            if pending_edu:
                m = edu_pattern_dates_only.search(ln)
                if m:
                    degree, inst = pending_edu
                    edu.append({
                        "start": m.group("start"),
                        "end": m.group("end"),
                        "degree": degree,
                        "institution": inst,
                        "status": "completed",
                    })
                    pending_edu = None
                    continue
                # tarih gelmediyse tek satır desenleri denemeye izin ver

            m = edu_pattern_bar.search(ln)
            if m:
                degree = re.sub(rf"{BULLET_RE}\s*", "", m.group(3).strip())
                inst = re.sub(rf"{BULLET_RE}\s*", "", m.group(4).strip())
                edu.append({
                    "start": m.group(1),
                    "end": m.group(2),
                    "degree": degree,
                    "institution": inst,
                    "status": "completed",
                })
                continue

            m = edu_pattern_dash.search(ln)
            if m:
                degree = re.sub(rf"{BULLET_RE}\s*", "", m.group("degree").strip())
                inst = re.sub(rf"{BULLET_RE}\s*", "", m.group("inst").strip())
                edu.append({
                    "start": m.group("start"),
                    "end": m.group("end"),
                    "degree": degree,
                    "institution": inst,
                    "status": "completed",
                })
                continue

            m = edu_pattern_deg_inst_comma.search(ln)
            if m:
                degree = re.sub(rf"{BULLET_RE}\s*", "", m.group("degree").strip())
                inst = re.sub(rf"{BULLET_RE}\s*", "", m.group("inst").strip())
                edu.append({
                    "start": m.group("start"),
                    "end": m.group("end"),
                    "degree": degree,
                    "institution": inst,
                    "status": "completed",
                })
                continue

            m = edu_pattern_comma.search(ln)
            if m:
                degree = re.sub(rf"{BULLET_RE}\s*", "", m.group("degree").strip())
                edu.append({
                    "start": m.group("start"),
                    "end": m.group("end"),
                    "degree": degree,
                    "institution": "",
                    "status": "completed",
                })
                continue

            m = edu_pattern_single.search(ln)
            if m:
                degree = re.sub(rf"{BULLET_RE}\s*", "", m.group("degree").strip())
                inst = re.sub(rf"{BULLET_RE}\s*", "", m.group("inst").strip())
                edu.append({
                    "start": m.group("single"),
                    "end": None,
                    "degree": degree,
                    "institution": inst,
                    "status": "completed",
                })
                continue

    # Son exp açıklamasını kapat
    if last_idx is not None and descr_buffer:
        exp[last_idx]["description"] = " ".join(descr_buffer).strip()

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

        exists = False
        if merge and (title or company or start_d or end_d):
            exists = Experience.objects.filter(
                cv=cv, title=title, company=company,
                start_date=start_d or None, end_date=end_d or None
            ).exists()
        if exists:
            continue

        Experience.objects.create(
            cv=cv, title=title, company=company,
            start_date=start_d, end_date=end_d, description=desc
        )
        added_exp += 1

    # Education
    for ed in (output.get("education") or []):
        start_d = _parse_my(ed.get("start") or "") if ed.get("start") else None
        end_d = _parse_my(ed.get("end") or "") if ed.get("end") else None
        degree = (ed.get("degree") or "").strip()
        inst = (ed.get("institution") or "").strip()

        exists = False
        if merge and (degree or inst or start_d or end_d):
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