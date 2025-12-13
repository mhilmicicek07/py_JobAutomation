from __future__ import annotations
from typing import Dict, List, Any
from datetime import date
import logging
import json

from django.conf import settings
from ai_bridge.providers import get_provider

logger = logging.getLogger(__name__)


# ── Yardımcı biçimlendiriciler ────────────────────────────────────────────────

def _fmt_dmy(d: date | None) -> str:
    if not d:
        return ""
    return d.strftime("%d.%m.%Y")

def _fmt_my(d: date | None) -> str:
    if not d:
        return ""
    return d.strftime("%m/%Y")

def _period_str(start, end) -> str:
    if start and not end:
        return f"seit {_fmt_my(start)}"
    if start and end:
        return f"{_fmt_my(start)} – {_fmt_my(end)}"
    if end:
        return _fmt_my(end)
    return ""

def _join_nonempty(parts: List[str], sep: str = " • ") -> str:
    return sep.join([p for p in parts if p])

def collect_process_facts(cv) -> List[str]:
    facts: List[str] = []
    for p in cv.processes.all():
        t = p.type
        if t == "WORK_PERMIT":
            facts.append(f"Arbeitsgenehmigung gültig bis {_fmt_my(p.end_date)}.")
        elif t == "UNPAID_LEAVE":
            facts.append(f"Seit {_fmt_my(p.start_date)} in unbezahltem Urlaub.")
        elif t == "RESIGNATION":
            facts.append(f"Kündigungsprozess abgeschlossen {_fmt_my(p.end_date)}; sofortige Einsatzbereitschaft.")
        elif t == "DL_UMSCHREIBEN":
            if p.status == "DONE":
                facts.append(f"Umschreibung des Führerscheins abgeschlossen am {_fmt_dmy(p.end_date)}.")
            else:
                facts.append(f"Umschreibung des Führerscheins seit {_fmt_dmy(p.start_date)} im Gange.")
        elif t == "DIPLOMA_EVAL":
            if p.status == "DONE":
                facts.append(f"Zeugnisbewertung abgeschlossen am {_fmt_dmy(p.end_date)}.")
            else:
                facts.append(f"Zeugnisbewertung seit {_fmt_dmy(p.start_date)} im Gange.")
        elif t == "BA_REG":
            d = p.end_date or p.start_date
            facts.append(f"Bei der Bundesagentur für Arbeit registriert seit {_fmt_my(d)}.")
    return facts


# ── ATS uyumlu CV bölümleri ───────────────────────────────────────────────────

def build_cv_sections(cv, posting) -> Dict[str, Any]:
    # Profil
    if cv.field == "WEB":
        profil = _join_nonempty([
            f"{cv.full_name} – Full-Stack Webentwickler (Python/Django, React).",
            "Fokus: REST-APIs, Datenmodellierung, Auth, Frontend-Integration.",
        ], " ")
    elif cv.field == "BWL":
        profil = _join_nonempty([
            f"{cv.full_name} – Finanzbuchhaltung / Controlling.",
            "Fokus: Kreditoren, Zahlungsverkehr, Kontenabstimmung, Monats-/Jahresabschluss (HGB).",
        ], " ")
    else:
        profil = f"{cv.full_name} – Berufliches Profil."

    # İlan becerilerini al
    post_skills: List[str] = []
    if hasattr(posting, "extracted_skills") and posting.extracted_skills:
        post_skills = posting.extracted_skills
    else:
        # Burada user=None gönderiyoruz çünkü build_cv_sections genellikle 
        # zaten analiz edilmiş ilanla çalışır. Tekrar AI çağırmaya gerek yok.
        # Gerekirse import edip çağırmak yerine posting.extracted_skills kullanılmalı.
        from job_analyzer import services as ja_services
        data = ja_services.extract_requirements(posting.raw_text, posting.target_field)
        post_skills = data.get("skills", []) or []
    
    need = {s.lower() for s in post_skills}

    # CV becerileri
    from cv_manager.models import Skill, Experience, Education
    all_skills = list(Skill.objects.filter(cv=cv).order_by("name").values_list("name", flat=True))
    
    matched = [s for s in all_skills if s.lower() in need]
    unmatched = [s for s in all_skills if s.lower() not in need]
    kenntnisse = ", ".join(matched + unmatched)
    
    diagnostik = {
        "matched_skills": matched,
        "missing_skills": [s for s in post_skills if s.lower() not in {x.lower() for x in all_skills}],
    }

    # Berufserfahrung
    exps = Experience.objects.filter(cv=cv).order_by("-end_date", "-start_date")
    need_lower = need 

    matched_lines, unmatched_lines = [], []
    for e in exps:
        zeitraum = _period_str(e.start_date, e.end_date)
        kopf = _join_nonempty([zeitraum, f"{e.title}", e.company], " | ")
        desc = (e.description or "").strip()
        line = kopf if not desc else f"{kopf}\n  • {desc}"

        text_for_match = f"{e.title} {e.company or ''} {desc}".lower()
        has_match = any(k in text_for_match for k in need_lower)

        (matched_lines if has_match else unmatched_lines).append(line)

    erfahrung = "\n".join(matched_lines + unmatched_lines)

    # Ausbildung
    edus = Education.objects.filter(cv=cv).order_by("-end_date", "-start_date")
    ausbildung_lines: List[str] = []
    for ed in edus:
        zeitraum = _join_nonempty([_fmt_my(ed.start_date), _fmt_my(ed.end_date)], " – ")
        line = _join_nonempty([zeitraum, ed.degree, ed.institution], " | ")
        ausbildung_lines.append(line)
    ausbildung = "\n".join(ausbildung_lines)

    # Hinweise
    hinweise = " ".join(collect_process_facts(cv))

    return {
        "profil": profil,
        "kenntnisse": kenntnisse,
        "erfahrung": erfahrung,
        "ausbildung": ausbildung,
        "hinweise": hinweise,
        "diagnostik": diagnostik,
    }


# ── Anschreiben üretimi (AI Provider Refactored) ──────────────────────────────

def build_cover_letter(cv, posting, user=None) -> str:
    """
    Almanca Anschreiben metni üretir.
    Eğer 'user' verilmişse ve AI ayarları yapılandırılmışsa AI (Provider) kullanır.
    Aksi halde veya hata durumunda şablon tabanlı (template) üretim yapar.
    """
    # 1) Veri Hazırlığı
    process_lines = collect_process_facts(cv)
    process_block = " ".join(process_lines) or "Ich bin zeitnah einsetzbar."
    
    skills: List[str] = []
    if hasattr(posting, "extracted_skills") and posting.extracted_skills:
        skills = posting.extracted_skills

    cv_sections = build_cv_sections(cv, posting)

    # 2) AI Denemesi (Eğer user varsa)
    ai_success = False
    ai_text = ""

    if user:
        try:
            # Sağlayıcıyı al (OpenAI, Gemini, Stub...)
            provider = get_provider(user)
            
            # StubProvider ise (API key yoksa) hiç deneme, template'e düş
            # (Provider'ın type'ını kontrol etmek yerine, extract_json çağırıp boş dönmesini bekleyebiliriz 
            # ama StubProvider log basıyor, temiz olsun diye burada kesebiliriz. 
            # Şimdilik doğrudan çağırıyoruz, Stub boş dict döner.)
            
            payload = {
                "job_posting_text": getattr(posting, "raw_text", ""),
                "target_field": getattr(posting, "target_field", ""),
                "posting_skills": skills,
                "cv_field": getattr(cv, "field", ""),
                "cv_full_name": getattr(cv, "full_name", ""),
                "cv_sections": cv_sections,
                "process_facts": process_lines,
            }

            system_prompt = (
                "Du bist ein deutscher Bewerbungscoach. "
                "Erstelle ein professionelles Anschreiben basierend auf den JSON-Daten (Stellenanzeige + Lebenslauf). "
                "Reagiere auf die Anforderungen der Stelle (job_posting_text) und matche sie mit den Stärken des Kandidaten (cv_sections). "
                "Verwende eine positive, motivierte Sprache. Erfinde keine Fakten. "
                "WICHTIG: Antworte als JSON-Objekt mit einem einzigen Schlüssel 'cover_letter', "
                "der den kompletten Text des Anschreibens enthält. Keine Markdown-Formatierung im Text."
            )

            # JSON String olarak gönderelim ki provider (extract_json) rahat işlesin
            input_text = json.dumps(payload, ensure_ascii=False)
            
            # Provider çağrısı
            response_data = provider.extract_json(input_text, system_prompt)
            
            # Yanıtı al
            if response_data and "cover_letter" in response_data:
                ai_text = response_data["cover_letter"]
                if ai_text and len(ai_text) > 50:
                    ai_success = True

        except Exception as e:
            logger.error(f"AI Cover Letter generation failed: {e}")
            # Fallback to template below

    if ai_success:
        return ai_text

    # ── Fallback: Klasik Template ─────────────────────────────────────────────
    
    logger.info("Falling back to template-based cover letter.")

    diagnostik = cv_sections.get("diagnostik") or {} # type: ignore
    matched = diagnostik.get("matched_skills") or [] # type: ignore
    missing = set(diagnostik.get("missing_skills") or []) # type: ignore

    # Skills Cümlesi
    skills_for_sentence = matched if matched else [s for s in skills if s not in missing]
    
    # Temizle ve birleştir
    cleaned = []
    seen = set()
    for s in skills_for_sentence:
        norm = s.strip()
        if norm and norm.lower() not in seen:
            seen.add(norm.lower())
            cleaned.append(norm)

    skills_sentence = ""
    if cleaned:
        short = cleaned[:6]
        if len(short) == 1:
            skills_sentence = f" Meine Schwerpunkte liegen unter anderem in {short[0]}."
        else:
            skills_sentence = (
                " Meine Schwerpunkte liegen unter anderem in " 
                + ", ".join(short[:-1]) + " und " + short[-1] + "."
            )

    # Giriş Paragrafı
    field = getattr(cv, "field", "")
    if field == "WEB":
        einleitung = (
            "Sehr geehrte Damen und Herren,\n\n"
            "mit großem Interesse bewerbe ich mich auf Ihre Position im Bereich Webentwicklung. "
            "Ich bringe praxisnahe Erfahrung mit Python/Django im Backend und modernen JavaScript-Frameworks im Frontend mit."
        )
    elif field == "BWL":
        einleitung = (
            "Sehr geehrte Damen und Herren,\n\n"
            "gerne bewerbe ich mich auf Ihre Position in der Finanzbuchhaltung. "
            "Ich verfüge über Erfahrung in der Kreditorenbuchhaltung und Monatsabschlüssen."
        )
    else:
        einleitung = (
            "Sehr geehrte Damen und Herren,\n\n"
            "hiermit bewerbe ich mich auf die ausgeschriebene Position."
        )

    kompetenz = (
        "Ich arbeite strukturiert und eigenverantwortlich. " 
        + (skills_sentence if skills_sentence else "")
    )

    verfuegbarkeit = process_block
    schluss = "Über die Möglichkeit eines persönlichen Gesprächs freue ich mich.\n\nMit freundlichen Grüßen"

    return "\n\n".join([einleitung, kompetenz, verfuegbarkeit, schluss])