from __future__ import annotations
from typing import Dict, List
from datetime import date

def _fmt_dmy(d: date | None) -> str:
    if not d:
        return ""
    return d.strftime("%d.%m.%Y")

def _fmt_my(d: date | None) -> str:
    if not d:
        return ""
    return d.strftime("%m/%Y")

def _join_nonempty(parts: List[str], sep: str = " • ") -> str:
    return sep.join([p for p in parts if p])

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
            # tarih hangi alanda tutulduysa tercih et
            d = p.end_date or p.start_date
            facts.append(f"Bei der Bundesagentur für Arbeit registriert seit {_fmt_my(d)}.")
    return facts

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

    # Kenntnisse
    from cv_manager.models import Skill, Experience, Education  # lazy import
    skills = Skill.objects.filter(cv=cv).order_by("name").values_list("name", flat=True)
    kenntnisse = ", ".join(skills)

    # Berufserfahrung
    exps = Experience.objects.filter(cv=cv).order_by("-end_date", "-start_date")
    erfahrung_lines: List[str] = []
    for e in exps:
        zeitraum = _join_nonempty([_fmt_my(e.start_date), _fmt_my(e.end_date)], " – ")
        kopf = _join_nonempty([zeitraum, f"{e.title}", e.company], " | ")
        desc = (e.description or "").strip()
        line = kopf if not desc else f"{kopf}\n  • {desc}"
        erfahrung_lines.append(line)
    erfahrung = "\n".join(erfahrung_lines)

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
    }

def build_cover_letter(cv, posting) -> str:
    """
    Almanca Anschreiben metni. İlan metnini (posting.raw_text) ve süreçleri (cv.processes) referans alır.
    Not: Selamlama ve şirket adı genel bırakıldı; kullanıcı düzenleyebilir.
    """
    process_lines = collect_process_facts(cv)
    process_block = " ".join(process_lines)

    # Çok genel bir kalıp, madde imi yok, kısa paragraflar
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
            "Ich verfüge über fundierte Erfahrung in der Kreditorenbuchhaltung, im Zahlungsverkehr und in der Abstimmung von Konten "
            "sowie in vorbereitenden Tätigkeiten für Monats- und Jahresabschlüsse nach HGB."
        )
    else:
        einleitung = (
            "Sehr geehrte Damen und Herren,\n\n"
            "hiermit bewerbe ich mich auf die ausgeschriebene Position. "
            "Ich bringe eine solide Kombination aus Fachkenntnissen und Praxis mit."
        )

    kompetenz = (
        "Relevante Kenntnisse entnehme ich der Ausschreibung und stelle sie passgenau bereit. "
        "Ich arbeite strukturiert, eigenverantwortlich und lege Wert auf saubere, nachvollziehbare Ergebnisse."
    )

    verfuegbarkeit = process_block or "Ich bin zeitnah einsetzbar."

    schluss = (
        "Über die Möglichkeit eines persönlichen Gesprächs freue ich mich. "
        "Mit freundlichen Grüßen"
    )

    letter = "\n\n".join([einleitung, kompetenz, verfuegbarkeit, schluss])
    return letter