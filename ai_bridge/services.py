from __future__ import annotations
from typing import Dict, Any

def ai_extract_posting(posting) -> Dict[str, Any]:
    """
    AI sağlayıcıya çağrı yapılacak yer.
    Şimdilik stub: job_analyzer.services.extract_requirements ile simüle ediyoruz.
    """
    from job_analyzer import services as ja_services
    data = ja_services.extract_requirements(posting.raw_text, posting.target_field)
    # İleride burada LLM çağrısı ve ek alan çıkarımı (title/company vb.) yapılacak.
    return {
        "skills": data.get("skills", []),
        "experience": data.get("experience", []),
        "target_field": posting.target_field,
    }