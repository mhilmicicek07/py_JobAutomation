import logging
from .providers import get_provider

logger = logging.getLogger(__name__)

def ai_extract_posting(posting, user):
    """
    İlan metnini (JobPosting) analiz eder.
    Kullanıcının seçtiği AI sağlayıcısını kullanır.
    """
    # 1. Kullanıcıya uygun sağlayıcıyı al
    provider = get_provider(user)
    
    # 2. İlan metni
    text = posting.raw_text
    if not text:
        return {}

    # 3. Sistem talimatı (Prompt)
    system_prompt = (
        "You are an expert technical recruiter. "
        "Extract skills (technologies, tools, languages) and experience requirements from the job description. "
        "Return a JSON object with keys: 'skills' (list of strings) and 'experience' (list of strings)."
    )

    try:
        # 4. Sağlayıcıdan JSON iste
        return provider.extract_json(text, system_prompt)
    except Exception as e:
        logger.error(f"AI extraction failed for posting {posting.id}: {e}")
        # Hata durumunda boş dict dön, böylece caller heuristik (regex) fallback'e düşebilir.
        return {}


def ai_extract_cv(cv_source, user):
    """
    CV metnini (CVSource) analiz eder.
    """
    # 1. Sağlayıcıyı al
    provider = get_provider(user)

    # 2. CV metni
    text = cv_source.raw_text
    if not text:
        return {}

    # 3. Prompt
    system_prompt = (
        "You are an expert CV parser. "
        "Extract the candidate's details into a structured JSON. "
        "Keys needed: "
        "'skills' (list of strings), "
        "'experience' (list of objects with keys: title, company, start, end, description), "
        "'education' (list of objects with keys: degree, institution, start, end, status)."
        "Dates should be in 'MM/YYYY' format if possible."
    )

    try:
        return provider.extract_json(text, system_prompt)
    except Exception as e:
        logger.error(f"AI extraction failed for CV source {cv_source.id}: {e}")
        return {}