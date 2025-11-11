# applicant_letters/services.py
from __future__ import annotations
from typing import Dict, List
from datetime import date


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

def build_cover_letter(cv, posting) -> str:
    """
    Almanca Anschreiben metni. İlan becerilerini (posting.extracted_skills) ve süreçleri (cv.processes)
    referans alır. Eğer extracted_skills boşsa, metinden yerinde çıkarım yapar.
    """
    # 1) Süreç bilgileri
    process_lines = collect_process_facts(cv)
    process_block = " ".join(process_lines) or "Ich bin zeitnah einsetzbar."

    # 2) İlan becerileri
    skills: List[str] = []
    if hasattr(posting, "extracted_skills") and posting.extracted_skills:
        skills = posting.extracted_skills
    else:
        from job_analyzer import services as ja_services  # lazy import
        data = ja_services.extract_requirements(posting.raw_text, posting.target_field)
        skills = data.get("skills", []) or []
    skills_snippet = _join_list(skills, max_n=3)  # en fazla 3 beceri vurgula
    skills_sentence = f"Besonders relevant finde ich: {skills_snippet}." if skills_snippet else ""

    # 3) Metin blokları (alan bazlı giriş)
    if cv.field == "WEB":
        einleitung = (
            "Sehr geehrte Damen und Herren,\n\n"
            "mit großem Interesse bewerbe ich mich auf Ihre Position im Bereich Webentwicklung. "
            "Ich bringe praxisnahe Erfahrung mit Python/Django im Backend und modernen JavaScript-Frameworks im Frontend mit. "
            "In Projekten habe ich REST-APIs konzipiert und implementiert, Datenmodelle aufgebaut und Schnittstellen stabil betrieben."
        )
    elif cv.field == "BWL":
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