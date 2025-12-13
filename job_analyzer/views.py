from __future__ import annotations

from typing import Any, Dict, List

from django import forms
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
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


@login_required
@require_http_methods(["GET", "POST"])
def quick_apply(request):
    result: Dict[str, Any] | None = None

    if request.method == "POST":
        form = QuickApplyForm(request.POST)
        if form.is_valid():
            raw_text = form.cleaned_data["raw_text"]
            target_field = form.cleaned_data["target_field"]

            # 1. İlanı kaydet
            posting = JobPosting.objects.create(
                raw_text=raw_text,
                target_field=target_field
            )

            # 2. AI veya Heuristik Analiz
            # GÜNCELLEME: request.user parametresi eklendi
            data = ai_services.ai_extract_posting(posting, user=request.user)

            # AI başarısız olduysa veya boş döndüyse fallback (heuristik)
            if not data.get("skills") and not data.get("experience"):
                data = ja_services.extract_requirements(raw_text, target_field)

            skills = data.get("skills") or []
            experience = data.get("experience") or []

            # Sonuçları kaydet
            posting.extracted_skills = skills
            posting.extracted_experience = experience
            
            # Skorlama
            cv = ja_services.get_primary_cv_or_fallback(target_field)
            score = ja_services.score_posting_against_cv(cv, skills)
            decision = ja_services.decision_from_score(score)

            posting.match_score = score
            posting.decision = decision
            posting.save()

            # 3. Ön Yazı (Cover Letter) & Taslak
            # GÜNCELLEME: user=request.user parametresini buraya ekledik
            cover_letter = letter_services.build_cover_letter(cv, posting, user=request.user)

            draft, _ = ApplicationDraft.objects.update_or_create(
                posting=posting,
                cv=cv,
                defaults={
                    "cover_letter": cover_letter,
                    "cv_sections": letter_services.build_cv_sections(cv, posting),
                    "language": "de"
                }
            )

            # 4. Sonuç Hazırlığı (Template için)
            section_labels = {
                "profil": "Profil",
                "kenntnisse": "Kenntnisse",
                "erfahrung": "Berufserfahrung",
                "ausbildung": "Ausbildung",
                "hinweise": "Sonstiges / Hinweise",
            }

            sections = []
            if isinstance(draft.cv_sections, dict):
                for key, value in draft.cv_sections.items():
                    if key == "diagnostik" or not isinstance(value, str):
                        continue

                    text = value.strip()

                    # Basit tekrar temizliği özellikle Erfahrung / Ausbildung için
                    if key in {"erfahrung", "ausbildung"}:
                        lines = [ln.rstrip() for ln in text.splitlines()]
                        seen = set()
                        deduped = []
                        for ln in lines:
                            if ln and ln not in seen:
                                seen.add(ln)
                                deduped.append(ln)
                        text = "\n".join(deduped).strip()

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