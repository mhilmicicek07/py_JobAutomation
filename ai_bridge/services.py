from __future__ import annotations
from typing import Dict, Any, List
from datetime import date
import re
import os
import json
import logging

from django.conf import settings

logger = logging.getLogger(__name__)


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


def _norm_range_token(token: str) -> str:
    """
    Ay isimleri vs gelirse çok basit normalize et.
    Örn:
      '03/2019' → '03/2019'
      '2019-03' → '03/2019'
    """
    token = (token or "").strip()
    m = re.match(r"^(\d{4})-(\d{2})$", token)
    if m:
        yyyy, mm = m.group(1), m.group(2)
        return f"{mm}/{yyyy}"
    return token


def _safe_int(text: str, default: int | None = None) -> int | None:
    try:
        return int(text)
    except (TypeError, ValueError):
        return default


def _shorten_skill(s: str) -> str:
    """
    Çok uzun gereksiz açıklamaları kırpar.
    Örn: 'Sehr gute Kenntnisse in Microsoft Excel' → 'excel'
    """
    s = (s or "").strip().lower()
    if "excel" in s:
        return "excel"
    if "python" in s:
        return "python"
    if "django" in s:
        return "django"
    if "rest api" in s or "rest-api" in s:
        return "rest api"
    if "sql" in s:
        return "sql"
    if "javascript" in s:
        return "javascript"
    if "react" in s:
        return "react"
    if "docker" in s:
        return "docker"
    if "linux" in s:
        return "linux"
    if "git" in s:
        return "git"
    if "unit test" in s or "unittest" in s:
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


LEADING_NOISE_RE = re.compile(r"^[\s\W_]+", re.UNICODE)


def _lstrip_symbols(s: str) -> str:
    """Başta yer alan boşluk, noktalama, bullet vb sembolleri temizle."""
    return LEADING_NOISE_RE.sub("", (s or "").strip())


# ── OpenAI yardımcıları (genel) ──────────────────────────────────────────────

def _get_openai_client():
    """
    Ortamdan OPENAI_API_KEY okuyup OpenAI client döner.
    Paket yüklü değilse veya key yoksa RuntimeError fırlatır.
    """
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError(
            "openai paketi yüklü değil. `pip install openai` çalıştır."
        ) from exc

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY ortam değişkeni set edilmemiş.")

    return OpenAI(api_key=api_key)


def _call_openai_json(instructions: str, user_input: str, model_setting_name: str) -> Dict[str, Any]:
    """
    JSON mode ile cevap dönen yardımcı.
    instructions → sistem rolü / açıklama,
    user_input → metnin kendisi (CV veya ilan).
    model_setting_name → settings içindeki model ayarının adı (örn. 'OPENAI_MODEL_POSTING').
    """
    provider = getattr(settings, "AI_PROVIDER", "stub")
    if provider != "openai":
        raise RuntimeError("AI_PROVIDER 'openai' değilken _call_openai_json çağrıldı.")

    client = _get_openai_client()
    model = (
        getattr(settings, model_setting_name, None)
        or getattr(settings, "OPENAI_DEFAULT_MODEL", "gpt-4o-mini")
    )

    resp = client.responses.create(
        model=model,
        response_format={"type": "json_object"},
        instructions=instructions,
        input=user_input,
    ) # type: ignore
    text = resp.output_text
    return json.loads(text)


# ── AI çıkarımı (POSTING) – OpenAI + heuristik fallback ──────────────────────

def ai_extract_posting(posting) -> Dict[str, Any]:
    """
    JobPosting için AI destekli çıkarım.

    - AI_PROVIDER == 'openai' ise OpenAI JSON extraction kullanır.
    - Diğer durumlarda eski heuristik extract_requirements'e düşer.
    """
    raw = posting.raw_text or ""
    target_field = getattr(posting, "target_field", "")

    provider = getattr(settings, "AI_PROVIDER", "stub")

    # OpenAI yolu
    if provider == "openai":
        instructions = (
            "You are an assistant that extracts requirements from German job postings "
            "and returns a JSON object with this schema:\n"
            "{\n"
            '  "skills": ["skill1", "skill2", ...],\n'
            '  "experience": ["sentence1", "sentence2", ...]\n'
            "}\n\n"
            "skills: distinct, lowercased skill or technology names (e.g. 'python', "
            "'sap fi', 'ms excel'), short strings. "
            "experience: short textual requirements or responsibilities as sentences. "
            "Respond with JSON only, no explanations."
        )
        try:
            data = _call_openai_json(
                instructions=instructions,
                user_input=raw,
                model_setting_name="OPENAI_MODEL_POSTING",
            )
            skills = data.get("skills") or []
            experience = data.get("experience") or []
        except Exception:
            logger.exception(
                "OpenAI job posting extraction failed; falling back to heuristics."
            )
            from job_analyzer import services as ja_services
            data = ja_services.extract_requirements(raw, target_field)
            skills = data.get("skills", [])
            experience = data.get("experience", [])
    else:
        # Eski davranış (stub / heuristik)
        from job_analyzer import services as ja_services
        data = ja_services.extract_requirements(raw, target_field)
        skills = data.get("skills", [])
        experience = data.get("experience", [])

    return {
        "skills": skills,
        "experience": experience,
        "target_field": target_field,
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
        "javascript", "react", "docker", "linux", "git", "unit test",
        "datev", "sap", "excel", "word", "powerpoint",
    ]
    skills_found: List[str] = []

    # Çok kabaca experience / education bloklarını ayrıştır
    exp: List[Dict[str, Any]] = []
    edu: List[Dict[str, Any]] = []

    # Deneyim ve eğitimde tarih aralıklarını (MM/YYYY - MM/YYYY) yakalayan regex
    range_pattern = re.compile(
        r"(?P<start>\d{2}/\d{4})\s*[-–]\s*(?P<end>\d{2}/\d{4}|heute|bis\s+heute|aktuell)",
        re.IGNORECASE,
    )
    single_date_pattern = re.compile(r"(?P<single>\d{2}/\d{4})")

    # Çok kaba başlık tespiti
    exp_headers = {"berufserfahrung", "erfahrung", "praxis", "praktische erfahrung"}
    edu_headers = {"ausbildung", "studium", "bildung", "schulausbildung"}

    mode = None  # "EXP" | "EDU" | None
    last_idx = None
    descr_buffer: List[str] = []

    # Education için basit pattern:
    edu_pattern_range = re.compile(
        r"^(?P<start>\d{2}/\d{4})\s*[-–]\s*(?P<end>\d{2}/\d{4})\s+(?P<degree>.+?),\s*(?P<inst>.+)$"
    )
    edu_pattern_single = re.compile(
        r"^(?P<single>\d{2}/\d{4})\s+(?P<degree>.+?),\s*(?P<inst>.+)$"
    )

    for idx, ln in enumerate(lines):
        lower = ln.lower()

        # Skills çıkarımı
        for tok in SKILL_TOKENS:
            if tok in lower:
                skills_found.append(_shorten_skill(tok))

        # Başlık anahtar kelimeleri
        if any(h in lower for h in exp_headers):
            mode = "EXP"
            continue
        if any(h in lower for h in edu_headers):
            mode = "EDU"
            continue

        # EXP / EDU blokları
        if mode == "EXP":
            m = range_pattern.search(ln)
            if m:
                start_t = _norm_range_token(m.group("start"))
                end_t = _norm_range_token(m.group("end"))
                start_d = _parse_my(start_t)
                end_d = None if "heute" in end_t.lower() else _parse_my(end_t)

                # Önceki exp açıklamasını kapat
                if last_idx is not None and descr_buffer:
                    exp[last_idx]["description"] = " ".join(descr_buffer).strip()
                    descr_buffer = []

                title = ln[m.end():].strip(" -–")
                exp.append(
                    {
                        "title": _lstrip_symbols(title),
                        "company": "",
                        "start": start_t if start_d else None,
                        "end": end_t if end_d or end_t else None,
                        "description": "",
                    }
                )
                last_idx = len(exp) - 1
                continue

            # Eğer tarih yoksa, mevcut experimente açıklama gibi ekle
            if last_idx is not None:
                descr_buffer.append(ln)
                continue

        elif mode == "EDU":
            m = edu_pattern_range.search(ln)
            if m:
                start_t = _norm_range_token(m.group("start"))
                end_t = _norm_range_token(m.group("end"))
                start_d = _parse_my(start_t)
                end_d = _parse_my(end_t)
                degree = _lstrip_symbols(m.group("degree"))
                inst = _lstrip_symbols(m.group("inst"))
                edu.append(
                    {
                        "start": start_t if start_d else None,
                        "end": end_t if end_d else None,
                        "degree": degree,
                        "institution": inst,
                        "status": "completed",
                    }
                )
                continue

            m = edu_pattern_single.search(ln)
            if m:
                degree = _lstrip_symbols(m.group("degree"))
                inst = _lstrip_symbols(m.group("inst"))
                edu.append(
                    {
                        "start": m.group("single"),
                        "end": None,
                        "degree": degree,
                        "institution": inst,
                        "status": "completed",
                    }
                )
                continue

    # Son exp açıklamasını kapat
    if last_idx is not None and descr_buffer:
        exp[last_idx]["description"] = " ".join(descr_buffer).strip()

    skills = _uniq_keep_order([_shorten_skill(s) for s in skills_found])

    return {"skills": skills, "experience": exp, "education": edu}


def _ai_extract_cv_openai(raw_text: str) -> Dict[str, Any]:
    """
    CV metnini OpenAI ile parse eder.

    Çıktı şeması:
    {
      "skills": ["python", "django", ...],
      "experience": [
        {
          "title": "...",
          "company": "...",
          "start": "MM/YYYY" veya None,
          "end": "MM/YYYY" veya None,
          "description": "kısa açıklama",
        },
        ...
      ],
      "education": [
        {
          "degree": "...",
          "institution": "...",
          "start": "MM/YYYY" veya None,
          "end": "MM/YYYY" veya None,
          "status": "completed" | "ongoing" | "unknown",
        },
        ...
      ],
    }
    """
    instructions = (
        "You are a CV parser. The user provides the full text of a CV in German, "
        "Turkish or English. You MUST respond with a single JSON object only, no extra text.\n\n"
        "Return a JSON object with keys: skills (array of strings), experience (array of objects with fields "
        "title, company, start, end, description), and education (array of objects with fields degree, institution, "
        "start, end, status). Use 'MM/YYYY' strings for dates or null when missing."
    )

    data = _call_openai_json(
        instructions=instructions,
        user_input=raw_text,
        model_setting_name="OPENAI_MODEL_CV",
    )

    # Güvenlik: en azından boş listeler dön
    return {
        "skills": data.get("skills") or [],
        "experience": data.get("experience") or [],
        "education": data.get("education") or [],
    }


def ai_extract_cv(cv_source) -> Dict[str, Any]:
    """
    CVSource.raw_text üzerinden AI destekli çıkarım.

    - AI_PROVIDER == 'openai' ise OpenAI tabanlı parser kullanır.
    - Diğer durumlarda mevcut heuristik ai_extract_cv_text'e düşer.
    """
    raw = cv_source.raw_text or ""
    provider = getattr(settings, "AI_PROVIDER", "stub")

    if provider == "openai":
        try:
            return _ai_extract_cv_openai(raw)
        except Exception:
            logger.exception(
                "OpenAI CV extraction failed; falling back to heuristics."
            )
            return ai_extract_cv_text(raw)
    else:
        return ai_extract_cv_text(raw)


# ── Snapshot’ı CV tablolarına uygulama ─────────────────────────────────────────

def apply_cv_snapshot(cv, snapshot) -> Dict[str, int]:
    """
    snapshot.output içindeki bilgileri CV'nin ilişkili tablolara uygular.
    Basit bir merging stratejisi: aynı kayıt varsa ekleme.
    """
    from cv_manager.models import Skill, Experience, Education

    output = snapshot.output or {}
    skills_data = output.get("skills") or []
    exp_data = output.get("experience") or []
    edu_data = output.get("education") or []

    added_skills = 0
    added_exp = 0
    added_edu = 0

    merge = True  # ileride ayar olabilir

    # Skills
    for sk in skills_data:
        sk_norm = (sk or "").strip()
        if not sk_norm:
            continue
        exists = False
        if merge:
            exists = Skill.objects.filter(cv=cv, name__iexact=sk_norm).exists()
        if exists:
            continue

        Skill.objects.create(cv=cv, name=sk_norm)
        added_skills += 1

    # Experience
    for item in exp_data:
        title = (item.get("title") or "").strip()
        company = (item.get("company") or "").strip()
        start_raw = item.get("start")
        end_raw = item.get("end")
        descr = (item.get("description") or "").strip()

        start_d = _parse_my(start_raw) if start_raw else None
        end_d = _parse_my(end_raw) if end_raw else None

        if not title and not company and not descr:
            continue

        exists = False
        if merge and title and company:
            exists = Experience.objects.filter(
                cv=cv,
                title__iexact=title,
                company__iexact=company,
                start_date=start_d or None,
                end_date=end_d or None,
            ).exists()
        if exists:
            continue

        Experience.objects.create(
            cv=cv,
            title=title,
            company=company,
            start_date=start_d,
            end_date=end_d,
            description=descr,
        )
        added_exp += 1

    # Education
    for item in edu_data:
        degree = (item.get("degree") or "").strip()
        inst = (item.get("institution") or "").strip()
        start_raw = item.get("start")
        end_raw = item.get("end")

        start_d = _parse_my(start_raw) if start_raw else None
        end_d = _parse_my(end_raw) if end_raw else None

        exists = False
        if merge and (degree or inst or start_d or end_d):
            exists = Education.objects.filter(
                cv=cv,
                degree=degree,
                institution=inst,
                start_date=start_d or None,
                end_date=end_d or None,
            ).exists()
        if exists:
            continue

        Education.objects.create(
            cv=cv,
            degree=degree,
            institution=inst,
            start_date=start_d,
            end_date=end_d,
        )
        added_edu += 1

    return {"skills": added_skills, "experience": added_exp, "education": added_edu}