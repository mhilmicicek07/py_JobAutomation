from __future__ import annotations

from typing import Any, Dict, List

from django import forms
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
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
        label="CV Alanı",
        initial="WEB",
        required=False,
        help_text="Welches CV soll für die Analyse verwendet werden?"
    )
    raw_text = forms.CharField(
        label="Stellenanzeige (Volltext)",
        widget=forms.Textarea(attrs={"rows": 16}),
        help_text="Komplette Anzeige hier einfügen (z. B. von einem Jobportal).",
    )
    
    def __init__(self, *args, user=None, cv_count=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Eğer sadece 1 CV varsa field seçimini gizle
        if cv_count == 1:
            self.fields['target_field'].widget = forms.HiddenInput()
            self.fields['target_field'].required = False


@login_required
def application_history(request):
    """Geçmiş başvuruları listeler."""
    drafts = ApplicationDraft.objects.select_related("cv", "posting").filter(
        cv__user=request.user
    ).order_by("-created_at")
    return render(request, "job_analyzer/history.html", {"drafts": drafts})


@login_required
def application_detail(request, pk):
    """Geçmiş bir başvurunun detayını gösterir."""
    draft = get_object_or_404(ApplicationDraft, pk=pk, cv__user=request.user)
    # Sonuçları quick_apply template yapısına uygun hazırlayalım
    result = {
        "posting": draft.posting,
        "cv": draft.cv,
        "skills": draft.posting.extracted_skills,
        "match_score": draft.posting.match_score,
        "score": draft.posting.match_score, # Template uyumu için
        "decision": draft.posting.decision,
        "cover_letter": draft.cover_letter,
        "draft": draft,
    }
    
    # Sections (Profil, Deneyim vb.) dict ise listeye çevir
    sections = []
    if isinstance(draft.cv_sections, dict):
        section_labels = {
            "profil": "Profil",
            "kenntnisse": "Kenntnisse",
            "erfahrung": "Berufserfahrung",
            "ausbildung": "Ausbildung",
            "hinweise": "Sonstiges / Hinweise",
        }
        for key, value in draft.cv_sections.items():
            if key == "diagnostik" or not isinstance(value, str):
                continue
            if value.strip():
                sections.append({
                    "key": key,
                    "label": section_labels.get(key, key.title()),
                    "text": value.strip()
                })
    
    result["sections"] = sections

    # Formu göstermeye gerek yok, sadece sonucu gösteriyoruz
    from cv_manager.models import CV
    user_cvs = CV.objects.filter(user=request.user)
    cv_count = user_cvs.count()
    
    return render(request, "job_analyzer/quick_apply.html", {
        "form": QuickApplyForm(user=request.user, cv_count=cv_count), # Boş form, hata vermemesi için
        "result": result,
        "readonly": True, # Template'de 'Analiz' butonunu gizlemek için kullanılabilir
        "cv_count": cv_count,
        "show_field_selection": cv_count > 1,
    })


@login_required
@require_http_methods(["GET", "POST"])
def quick_apply(request):
    from cv_manager.models import CV
    
    result: Dict[str, Any] | None = None
    
    # Kullanıcının CV sayısını kontrol et
    user_cvs = CV.objects.filter(user=request.user)
    cv_count = user_cvs.count()
    show_field_selection = cv_count > 1

    if request.method == "POST":
        form = QuickApplyForm(request.POST, user=request.user, cv_count=cv_count)
        if form.is_valid():
            raw_text = form.cleaned_data["raw_text"]
            target_field = form.cleaned_data.get("target_field", "GEN")

            if cv_count == 0:
                messages.error(request, "Önce en az bir CV oluşturmalısınız.")
                return render(
                    request,
                    "job_analyzer/quick_apply.html",
                    {
                        "form": form,
                        "result": None,
                        "cv_count": cv_count,
                        "show_field_selection": show_field_selection,
                    },
                )

            # 1. İlanı kaydet
            posting = JobPosting.objects.create(
                raw_text=raw_text,
                target_field=target_field
            )

            # CV'yi al
            cv = ja_services.get_primary_cv_or_fallback(target_field, user=request.user)
            if not cv:
                messages.error(request, "Seçili alana uygun bir CV bulunamadı.")
                return render(
                    request,
                    "job_analyzer/quick_apply.html",
                    {
                        "form": form,
                        "result": None,
                        "cv_count": cv_count,
                        "show_field_selection": show_field_selection,
                    },
                )

            cv_text = cv.get_full_text()  # CV'nin tüm detaylarını içeren kapsamlı metin

            # 1. Önce AI ile tam karşılaştırma dene
            comparison = ai_services.ai_compare_cv_job(cv_text, raw_text, user=request.user)

            # AI başarılı oldu mu kontrol et
            if comparison.get("match_score", 0) > 0 and comparison.get("reasoning"):
                # AI başarılı - AI sonuçlarını kullan
                skills = comparison.get("matched_skills", [])
                experience = []  # AI karşılaştırma için gerekli değil
                score = comparison.get("match_score", 0)
                reasoning = comparison.get("reasoning", "")
                decision = comparison.get("decision", "REVIEW")

                print("✅ AI Comparison Successful")
            else:
                # AI başarısız - Heuristic fallback kullan
                print("⚠️ AI Comparison Failed, Using Heuristic Fallback")

                # Heuristic ile beceri çıkar
                heuristic_data = ja_services.extract_requirements(raw_text, target_field)
                skills = heuristic_data.get("skills", [])
                experience = heuristic_data.get("experience", [])

                # Eski yöntemle skor hesapla
                score = ja_services.score_posting_against_cv(cv, skills)
                decision = ja_services.decision_from_score(score)
                reasoning = f"Fallback: Heuristic analysis - {len(skills)} skills extracted"

            # Debug
            print(f"Final Result: Score={score}, Decision={decision}")
            print(f"Reasoning: {reasoning}")
            print(f"Skills: {skills}")

            posting.extracted_skills = skills
            posting.extracted_experience = experience

            posting.match_score = score
            posting.decision = decision
            posting.save()

            # 3. Ön Yazı & Taslak
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

            # 4. Sonuç Hazırlığı
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
                        sections.append({
                            "key": key,
                            "label": section_labels.get(key, key.title()),
                            "text": text,
                        })

            result = {
                "posting": posting,
                "cv": cv,
                "skills": skills,
                "experience": experience,
                "match_score": score,
                "score": score,  # DÜZELTME: Template {{ result.score }} bekliyor
                "decision": decision,
                "sections": sections,
                "cover_letter": cover_letter,
                "draft": draft,
            }
    else:
        form = QuickApplyForm(user=request.user, cv_count=cv_count)

    return render(
        request,
        "job_analyzer/quick_apply.html",
        {
            "form": form,
            "result": result,
            "cv_count": cv_count,
            "show_field_selection": show_field_selection,
        },
    )
