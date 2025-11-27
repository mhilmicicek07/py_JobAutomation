from __future__ import annotations

from typing import Any, Dict, List

from django import forms
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from .models import JobPosting
from . import services as ja_services
from ai_bridge import services as ai_services
from applicant_letters import services as letter_services
from applicant_letters.models import ApplicationDraft


class QuickApplyForm(forms.Form):
    FIELD_CHOICES = [
        ("WEB", "Webentwicklung / IT"),
        ("BWL", "BWL / Finanzen"),
        ("GEN", "Allgemein / Sonstiges"),
    ]

    target_field = forms.ChoiceField(
        choices=FIELD_CHOICES,
        label="Zielbereich",
        initial="WEB",
    )
    raw_text = forms.CharField(
        label="Stellenanzeige (Volltext)",
        widget=forms.Textarea(attrs={"rows": 16}),
        help_text="Komplette Anzeige hier einfügen (z. B. von einem Jobportal).",
    )


@require_http_methods(["GET", "POST"])
def quick_apply(request):
    result: Dict[str, Any] | None = None

    if request.method == "POST":
        form = QuickApplyForm(request.POST)
        if form.is_valid():
            raw_text = form.cleaned_data["raw_text"]
            target_field = form.cleaned_data["target_field"]

            # 1) JobPosting kaydı
            posting = JobPosting.objects.create(
                raw_text=raw_text,
                target_field=target_field,
            )

            # 2) AI ile ilan gereksinimlerini çıkar
            try:
                ai_data = ai_services.ai_extract_posting(posting)
                skills: List[str] = ai_data.get("skills") or []
                experience = ai_data.get("experience") or []
            except Exception:
                data = ja_services.extract_requirements(raw_text, target_field)
                skills = data.get("skills", [])
                experience = data.get("experience", [])

            posting.extracted_skills = skills
            posting.extracted_experience = experience

            # 3) Uygun CV’yi seç, skor ve karar üret
            cv = ja_services.get_primary_cv_or_fallback(target_field)
            if cv:
                score = ja_services.score_posting_against_cv(cv, skills)
                decision = ja_services.decision_from_score(score)
            else:
                score = None
                decision = "REVIEW"

            posting.match_score = score
            posting.decision = decision
            posting.save(
                update_fields=[
                    "extracted_skills",
                    "extracted_experience",
                    "match_score",
                    "decision",
                    "updated_at",
                ]
            )

            cv_sections: Dict[str, str] = {}
            cover_letter = ""
            draft: ApplicationDraft | None = None

            # 4) CV bölümleri + Anschreiben
            if cv:
                cv_sections = letter_services.build_cv_sections(cv, posting)
                cover_letter = letter_services.build_cover_letter(cv, posting)

                draft, _ = ApplicationDraft.objects.update_or_create(
                    posting=posting,
                    cv=cv,
                    defaults={
                        "cv_sections": cv_sections,
                        "cover_letter": cover_letter,
                        "language": "de",
                    },
                )

            section_labels = {
                "profil": "Profil / Zusammenfassung",
                "kenntnisse": "Fachliche Stärken & Kenntnisse",
                "erfahrung": "Berufserfahrung (ATS-Text)",
                "ausbildung": "Ausbildung / Studium",
                "hinweise": "Hinweise / Rahmenbedingungen",
                "diagnostik": "Diagnostik / Meta",
            }
            sections = []
            for key in ["profil", "kenntnisse", "erfahrung", "ausbildung", "hinweise", "diagnostik"]:
                text = (cv_sections or {}).get(key, "").strip()
                if text:
                    sections.append(
                        {
                            "key": key,
                            "label": section_labels.get(key, key.title()),
                            "text": text,
                        }
                    )

            result = {
                "posting": posting,
                "cv": cv,
                "skills": skills,
                "experience": experience,
                "match_score": score,
                "decision": decision,
                "sections": sections,
                "cover_letter": cover_letter,
                "draft": draft,
            }
    else:
        form = QuickApplyForm()

    return render(
        request,
        "job_analyzer/quick_apply.html",
        {
            "form": form,
            "result": result,
        },
    )