import logging
import datetime
from .providers import get_provider
from cv_manager.models import Skill, Experience, Education

logger = logging.getLogger(__name__)

# ── 1. BÖLÜM: AI ÇAĞRILARI (EXTRACT) ──────────────────────────────────────────

def ai_extract_posting(posting, user):
    """
    İlan metnini analiz eder.
    """
    provider = get_provider(user)
    
    text = posting.raw_text
    if not text:
        return {}

    system_prompt = (
        "You are an expert technical recruiter. "
        "Extract skills (technologies, tools, languages) and experience requirements from the job description. "
        "Return a JSON object with keys: 'skills' (list of strings) and 'experience' (list of strings)."
    )

    try:
        return provider.extract_json(text, system_prompt)
    except Exception as e:
        logger.error(f"AI extraction failed for posting {posting.id}: {e}")
        return {}


def ai_extract_cv(cv_source, user):
    """
    CV metnini analiz eder.
    """
    provider = get_provider(user)

    text = cv_source.raw_text
    if not text:
        return {}

    system_prompt = (
        "You are an expert CV parser. "
        "Extract the candidate's details into a structured JSON. "
        "Keys needed: "
        "'skills' (list of strings), "
        "'experience' (list of objects with keys: title, company, start, end, description), "
        "'education' (list of objects with keys: degree, institution, start, end, status)."
        "Dates should be in 'MM/YYYY' format if possible. If currently working, set end to 'Present'."
    )

    try:
        return provider.extract_json(text, system_prompt)
    except Exception as e:
        logger.error(f"AI extraction failed for CV source {cv_source.id}: {e}")
        return {}


# ── 2. BÖLÜM: VERİTABANI İŞLEMLERİ (APPLY) ────────────────────────────────────

def _parse_date_str(date_str):
    """
    'MM/YYYY', 'YYYY-MM', 'YYYY' formatlarını Python date objesine çevirir.
    Hatalı formatta None döner.
    """
    if not date_str or str(date_str).lower() in ["present", "heute", "current"]:
        return None
    
    # Olası formatlar
    formats = ["%m/%Y", "%Y-%m", "%Y", "%m.%Y"]
    
    for fmt in formats:
        try:
            return datetime.datetime.strptime(str(date_str).strip(), fmt).date()
        except ValueError:
            continue
    return None

def apply_cv_snapshot(cv, snapshot, merge=False):
    """
    AI çıktısını (JSON) alır ve CV'ye ait Skill, Experience, Education kayıtlarını oluşturur.
    merge=False ise önce eskileri siler (temiz sayfa).
    """
    # View tarafında SimpleNamespace veya Model objesi gelebilir, output'u alalım
    data = getattr(snapshot, "output", {}) or {}
    
    if not data:
        return {"skills": 0, "experience": 0, "education": 0}

    # 1. Skills
    new_skills = data.get("skills", [])
    if new_skills:
        if not merge:
            Skill.objects.filter(cv=cv).delete()
        
        # Tekrarı önlemek için mevcutları al
        existing = set(Skill.objects.filter(cv=cv).values_list("name", flat=True))
        
        to_create = []
        for s in new_skills:
            if isinstance(s, str) and s not in existing:
                to_create.append(Skill(cv=cv, name=s.strip()))
                existing.add(s) # Aynı döngüde tekrar eklememek için
        
        Skill.objects.bulk_create(to_create)

    # 2. Experience
    exps = data.get("experience", [])
    created_exps = 0
    if exps:
        if not merge:
            Experience.objects.filter(cv=cv).delete()
        
        for exp in exps:
            title = exp.get("title", "Position")
            company = exp.get("company", "")
            desc = exp.get("description", "")
            start = _parse_date_str(exp.get("start"))
            end = _parse_date_str(exp.get("end"))
            
            Experience.objects.create(
                cv=cv,
                title=title,
                company=company,
                description=desc,
                start_date=start,
                end_date=end
            )
            created_exps += 1

    # 3. Education
    edus = data.get("education", [])
    created_edus = 0
    if edus:
        if not merge:
            Education.objects.filter(cv=cv).delete()
            
        for edu in edus:
            degree = edu.get("degree", "Abschluss")
            institution = edu.get("institution", "")
            start = _parse_date_str(edu.get("start"))
            end = _parse_date_str(edu.get("end"))
            status = edu.get("status", "DONE") # Varsayılan DONE
            
            # Status mapping
            if isinstance(status, str) and status.lower() in ["ongoing", "current", "laufend"]:
                status = "ONGOING"
            else:
                status = "DONE"

            Education.objects.create(
                cv=cv,
                degree=degree,
                institution=institution,
                start_date=start,
                end_date=end,
                status=status
            )
            created_edus += 1

    return {
        "skills": len(new_skills),
        "experience": created_exps,
        "education": created_edus
    }