from django.contrib import admin, messages
from django.utils.html import format_html
from .models import JobPosting
from . import services
from ai_bridge.models import ExtractionSnapshot
from ai_bridge import services as ai_services
from applicant_letters.models import ApplicationDraft
from applicant_letters import services as letter_services


@admin.action(description="🔍 İlanı AI ile analiz et ve puanla")
def analyze_postings_with_ai(modeladmin, request, queryset):
    """AI kullanarak ilan analizi yapar"""
    ok = 0
    for obj in queryset:
        # AI extraction dene
        data = ai_services.ai_extract_posting(obj, user=request.user)
        
        # AI başarısız olursa heuristic'e düş
        if not data.get("skills"):
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
        obj.save(
            update_fields=[
                "extracted_skills",
                "extracted_experience",
                "match_score",
                "decision",
                "updated_at",
            ]
        )
        ok += 1

    messages.success(request, f"{ok} ilan analiz edildi ve puanlandı.")


@admin.action(description="📝 İlanı sadece heuristik ile analiz et")
def analyze_postings_heuristic(modeladmin, request, queryset):
    """Sadece heuristic parser kullanır (AI yok)"""
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
        obj.save(
            update_fields=[
                "extracted_skills",
                "extracted_experience",
                "match_score",
                "decision",
                "updated_at",
            ]
        )
        ok += 1

    messages.success(request, f"{ok} ilan heuristik ile analiz edildi.")


@admin.action(description="✍️ Taslak oluştur (CV bölümleri + Anschreiben)")
def create_application_drafts(modeladmin, request, queryset):
    created_count = 0
    for obj in queryset:
        cv = services.get_primary_cv_or_fallback(obj.target_field)
        
        cover_letter = letter_services.build_cover_letter(cv, obj, user=request.user)
        cv_sections = letter_services.build_cv_sections(cv, obj)

        ApplicationDraft.objects.update_or_create(
            posting=obj,
            cv=cv,
            defaults={
                "cover_letter": cover_letter,
                "cv_sections": cv_sections,
                "language": "de",
            },
        )
        created_count += 1

    messages.success(request, f"{created_count} taslak oluşturuldu/güncellendi.")


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ("id", "get_field_badge", "get_score_display", "get_decision_badge", "created_at")
    list_filter = ("target_field", "decision", "created_at")
    search_fields = ("raw_text", "extracted_skills")
    readonly_fields = ("created_at", "updated_at", "preview_text", "preview_extracted")
    date_hierarchy = "created_at"
    actions = [analyze_postings_with_ai, analyze_postings_heuristic, create_application_drafts]
    
    def get_field_badge(self, obj):
        """Hedef alanı badge olarak göster"""
        colors = {"WEB": "info", "BWL": "warning", "GEN": "secondary"}
        color = colors.get(obj.target_field, "secondary")
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color, obj.get_target_field_display()
        )
    get_field_badge.short_description = "Alan"
    
    def get_score_display(self, obj):
        """Skoru renkli göster"""
        if obj.match_score is None:
            return "-"
        
        if obj.match_score >= 80:
            color = "green"
        elif obj.match_score >= 50:
            color = "orange"
        else:
            color = "red"
        
        return format_html(
            '<strong style="color: {};">{}/100</strong>',
            color, obj.match_score
        )
    get_score_display.short_description = "Skor"
    
    def get_decision_badge(self, obj):
        """Kararı badge olarak göster"""
        if not obj.decision:
            return "-"
        
        colors = {"APPLY": "success", "REVIEW": "warning", "SKIP": "danger"}
        color = colors.get(obj.decision, "secondary")
        
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color, obj.decision
        )
    get_decision_badge.short_description = "Karar"
    
    def preview_text(self, obj):
        """İlan metninin önizlemesi"""
        return format_html('<pre style="white-space: pre-wrap; max-height: 200px; overflow: auto;">{}</pre>', obj.raw_text[:500])
    preview_text.short_description = "İlan Metni"
    
    def preview_extracted(self, obj):
        """Çıkarılan bilgilerin önizlemesi"""
        skills_html = ", ".join(f"<span class='badge bg-info'>{s}</span>" for s in obj.extracted_skills[:10])
        return format_html('<div><strong>Skills:</strong><br>{}</div>', skills_html if skills_html else "-")
    preview_extracted.short_description = "Çıkarılan Bilgiler"