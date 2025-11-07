from django.contrib import admin, messages
from .models import JobPosting
from . import services

@admin.action(description="İlanı analiz et ve puanla")
def analyze_postings(modeladmin, request, queryset):
    ok = 0
    for obj in queryset:
        # 1) İlan metninden gereksinimleri çıkar
        data = services.extract_requirements(obj.raw_text, obj.target_field)
        skills = data.get("skills", [])
        experience = data.get("experience", [])

        # 2) Uygun CV’yi seç
        cv = services.get_primary_cv_or_fallback(obj.target_field)

        # 3) Skoru hesapla
        score = services.score_posting_against_cv(cv, skills)

        # 4) Kaydet
        obj.extracted_skills = skills
        obj.extracted_experience = experience
        obj.match_score = score
        obj.save(update_fields=["extracted_skills", "extracted_experience", "match_score", "updated_at"])
        ok += 1

    messages.success(request, f"{ok} ilan analiz edildi ve puanlandı.")

@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ("id", "target_field", "match_score", "created_at")
    list_filter = ("target_field",)
    search_fields = ("raw_text",)
    readonly_fields = ("created_at", "updated_at")
    actions = [analyze_postings]
