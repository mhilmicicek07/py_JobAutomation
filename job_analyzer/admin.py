from django.contrib import admin, messages
from .models import JobPosting
from . import services

@admin.action(description="İlanı analiz et ve puanla")
def analyze_postings(modeladmin, request, queryset):
    ok = 0
    for obj in queryset:
        data = services.extract_requirements(obj.raw_text, obj.target_field)
        skills = data.get("skills", [])
        experience = data.get("experience", [])
        cv = services.get_primary_cv_or_fallback(obj.target_field)
        score = services.score_posting_against_cv(cv, skills)
        decision = services.decision_from_score(score)

        obj.extracted_skills = skills
        obj.extracted_experience = experience
        obj.match_score = score
        obj.decision = decision
        obj.save(update_fields=[
            "extracted_skills",
            "extracted_experience",
            "match_score",
            "decision",
            "updated_at",
        ])
        ok += 1
    messages.success(request, f"{ok} ilan analiz edildi ve puanlandı.")


@admin.action(description="Taslak oluştur (CV bölümleri + Anschreiben)")
def create_application_drafts(modeladmin, request, queryset):
    # applicant_letters servislerini içeri al
    from applicant_letters.models import ApplicationDraft
    from applicant_letters import services as letter_services

    ok = 0
    for obj in queryset:
        # 1) Uygun CV'yi seç
        cv = services.get_primary_cv_or_fallback(obj.target_field)
        if not cv:
            continue

        # 2) Bölüm ve mektup üret
        sections = letter_services.build_cv_sections(cv, obj)
        letter = letter_services.build_cover_letter(cv, obj)

        # 3) Taslağı oluştur / güncelle
        draft, _created = ApplicationDraft.objects.get_or_create(posting=obj, cv=cv)
        draft.cv_sections = sections
        draft.cover_letter = letter
        draft.language = "de"
        draft.save(update_fields=["cv_sections", "cover_letter", "language", "updated_at"])
        ok += 1

    messages.success(request, f"{ok} taslak oluşturuldu/güncellendi.")


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ("id", "target_field", "match_score", "decision", "created_at")
    list_filter = ("target_field", "decision")
    search_fields = ("raw_text",)
    readonly_fields = ("created_at", "updated_at")
    actions = [analyze_postings, create_application_drafts]