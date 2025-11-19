from __future__ import annotations
from typing import Dict, List
from datetime import date
import os
import json
import logging

from django.conf import settings

logger = logging.getLogger(__name__)


# ── Yardımcı biçimlendiriciler ────────────────────────────────────────────────

def _fmt_dmy(d: date | None) -> str:
    """Gün.Ay.Yıl biçimi."""
    if not d:
        return ""
    return d.strftime("%d.%m.%Y")


def _fmt_my(d: date | None) -> str:
    """Ay/Yıl biçimi."""
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
    """Boş olmayan parçaları birleştir."""
    return sep.join([p for p in parts if p])


def _join_list(items: List[str], max_n: int = 3) -> str:
    """Listeyi virgülle birleştir, en fazla max_n öğe göster."""
    items = [i for i in items if i]
    if not items:
        return ""
    return ", ".join(items[:max_n])


# ── Süreç bilgilerini topla (Process modeli) ──────────────────────────────────

def collect_process_facts(cv) -> List[str]:
    """
    cv_manager.Process kayıtlarından Almanca kısa bilgilendirme cümleleri üretir.
    """
    from cv_manager.models import Process  # lazy import
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

def build_cv_sections(cv, posting) -> Dict[str, str]:
    """
    ATS uyumlu, kopyalanabilir Almanca bölümler üretir.
    """
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

    # Kenntnisse (ilandaki beceriler öne)
    from cv_manager.models import Skill, Experience, Education  # lazy import
    from job_analyzer import services as ja_services            # ilan becerileri için

    # İlan becerileri (analiz edilmişse onu kullan; yoksa yerinde çıkar)
    post_skills: List[str] = []
    if hasattr(posting, "extracted_skills") and posting.extracted_skills:
        post_skills = posting.extracted_skills
    else:
        data = ja_services.extract_requirements(posting.raw_text, posting.target_field)
        post_skills = data.get("skills", []) or []
    need = {s.lower() for s in post_skills}

    # CV becerileri
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

    # İlan becerileri kümesi (üstte zaten post_skills/need hesaplandı)
    need_lower = need  # {skill.lower() ...}

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

    # Hinweise (dinamik süreçler)
    hinweise = " ".join(collect_process_facts(cv))

    return {
        "profil": profil,
        "kenntnisse": kenntnisse,
        "erfahrung": erfahrung,
        "ausbildung": ausbildung,
        "hinweise": hinweise,
        "diagnostik": diagnostik, # type: ignore
    }


# ── Anschreiben üretimi ───────────────────────────────────────────────────────

def _build_cover_letter_openai(cv, posting, skills, process_lines, cv_sections) -> str:
    """
    OpenAI Responses API ile Almanca Anschreiben üretir.
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

    client = OpenAI(api_key=api_key)
    model = (
        getattr(settings, "OPENAI_MODEL_LETTER", None)
        or getattr(settings, "OPENAI_DEFAULT_MODEL", "gpt-4o-mini")
    )

    payload = {
        "job_posting_text": getattr(posting, "raw_text", ""),
        "target_field": getattr(posting, "target_field", ""),
        "posting_skills": list(skills or []),
        "cv_field": getattr(cv, "field", ""),
        "cv_full_name": getattr(cv, "full_name", ""),
        "cv_sections": cv_sections,
        "process_facts": process_lines,
    }

    instructions = (
    "Du bist ein deutscher Bewerbungscoach. "
    "Lies die JSON-Daten in der Eingabe (job_posting_text, cv_sections, process_facts). "
    "Schreibe ein vollständiges Anschreiben für eine Bewerbung in Deutschland. "
    "Sprich den Arbeitgeber mit der formellen Anrede ('Sie') an. "
    "Wenn im job_posting_text eine konkrete Kontaktperson (z.B. 'Frau Müller') klar erkennbar ist, "
    "verwende 'Sehr geehrte Frau Müller,' oder 'Sehr geehrter Herr ...'. "
    "Sonst verwende 'Sehr geehrte Damen und Herren,'. "
    "Gehe auf die wichtigsten Anforderungen der Stelle ein und verbinde sie mit den Erfahrungen und Kenntnissen "
    "aus cv_sections. Nutze process_facts (z.B. Arbeitsgenehmigung, Zeugnisbewertung, Verfügbarkeit), wenn sinnvoll. "
    "Verwende NUR Informationen, die in den JSON-Daten enthalten sind; erfinde keine zusätzlichen Stationen, "
    "Qualifikationen oder Defizite. "
    "Formuliere das Anschreiben GRUNDSÄTZLICH POSITIV: betone passende Erfahrungen, Lernbereitschaft und Motivation. "
    "Schreibe KEINE Sätze wie 'ich habe keine Erfahrung mit ...', 'mir fehlt ...' oder ähnliche Formulierungen, "
    "die den Bewerber schwächer wirken lassen. "
    "Wenn Technologien aus der Stellenanzeige im Lebenslauf nicht explizit vorkommen, kannst du sie höchstens als "
    "Lernziel oder Interesse erwähnen (z.B. 'ich baue meine Kenntnisse in X weiter aus'), aber nicht als Mangel. "
    "Antworte NUR mit dem finalen Anschreiben als Klartext, ohne Erklärungen und ohne JSON."
)

    resp = client.responses.create(
        model=model,
        instructions=instructions,
        input=json.dumps(payload, ensure_ascii=False),
    )
    return (resp.output_text or "").strip()

def build_cover_letter(cv, posting) -> str:
    """
    Almanca Anschreiben metni. İlan becerilerini (posting.extracted_skills) ve süreçleri (cv.processes)
    referans alır. Eğer extracted_skills boşsa, metinden yerinde çıkarım yapar.
    OpenAI etkinse (AI_COVER_LETTER_PROVIDER veya AI_PROVIDER 'openai' ise) önce AI ile üretmeyi dener,
    hata olursa klasik template'e düşer.
    """
    # 1) Süreç bilgileri (Verfügbarkeit vb.)
    process_lines = collect_process_facts(cv)
    process_block = " ".join(process_lines) or "Ich bin zeitnah einsetzbar."

    # 2) İlan becerileri
    skills: List[str] = []
    if hasattr(posting, "extracted_skills") and posting.extracted_skills:
        skills = posting.extracted_skills
    else:
        from job_analyzer import services as ja_services  # lazy import
        data = ja_services.extract_requirements(posting.raw_text, posting.target_field)
        skills = data.get("skills", []) if isinstance(data, dict) else (data or [])

    # 3) CV bölümleri (profil, kenntnisse, berufserfahrung)
    cv_sections = build_cv_sections(cv, posting)

    # 3a) AI yolu – yalnızca provider 'openai' ise dene
    provider = getattr(settings, "AI_COVER_LETTER_PROVIDER", None) or getattr(
        settings, "AI_PROVIDER", "stub"
    )
    if provider == "openai":
        try:
            return _build_cover_letter_openai(
                cv=cv,
                posting=posting,
                skills=skills,
                process_lines=process_lines,
                cv_sections=cv_sections,
            )
        except Exception:
            logger.exception(
                "OpenAI cover letter generation failed; falling back to template."
            )
            # Buradan sonra klasik template kodu çalışmaya devam edecek

    # ── Klasik template tabanlı Anschreiben ───────────────────────────────────

    # Becerileri kısaca bir cümleye dök
    skills_sentence = ""
    if skills:
        # 5–6 beceriyi geçmesin
        max_skills = 6
        short_list = [s for s in skills][:max_skills]
        skills_sentence = (
            " Meine Schwerpunkte liegen unter anderem in "
            + ", ".join(short_list[:-1])
            + (" und " + short_list[-1] if len(short_list) > 1 else short_list[0])
            + "."
        )

    # CV alanına göre giriş paragrafı
    field = getattr(cv, "field", "")
    if field == "WEB":
        einleitung = (
            "Sehr geehrte Damen und Herren,\n\n"
            "mit großem Interesse bewerbe ich mich auf Ihre Position im Bereich Webentwicklung. "
            "Ich bringe praxisnahe Erfahrung mit Python/Django im Backend und modernen JavaScript-Frameworks im Frontend mit. "
            "In Projekten habe ich REST-APIs konzipiert und implementiert, Datenmodelle aufgebaut und Schnittstellen stabil betrieben."
        )
    elif field == "BWL":
        einleitung = (
            "Sehr geehrte Damen und Herren,\n\n"
            "gerne bewerbe ich mich auf Ihre Position in der Finanzbuchhaltung. "
            "Ich verfüge über Erfahrung in der Kreditorenbuchhaltung, im Zahlungsverkehr und in der Abstimmung von Konten "
            "sowie in vorbereitenden Tätigkeiten für Monats- und Jahresabschlüsse nach HGB."
        )
    else:
        einleitung = (
            "Sehr geehrte Damen und Herren,\n\n"
            "hiermit bewerbe ich mich auf die ausgeschriebene Position. "
            "Ich bringe eine solide Kombination aus Fachkenntnissen und Praxis mit."
        )

    kompetenz = (
        "Ich arbeite strukturiert, eigenverantwortlich und lege Wert auf nachvollziehbare Ergebnisse. "
        + (skills_sentence if skills_sentence else "")
    )

    verfuegbarkeit = process_block
    schluss = "Über die Möglichkeit eines persönlichen Gesprächs freue ich mich.\n\nMit freundlichen Grüßen"

    letter = "\n\n".join([einleitung, kompetenz, verfuegbarkeit, schluss])
    return letter