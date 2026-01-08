from django.contrib import admin
from django.utils.html import format_html
from .models import ApplicationDraft

# Register your models here.
@admin.register(ApplicationDraft)
class ApplicationDraftAdmin(admin.ModelAdmin):
    list_display = ("id", "get_posting_preview", "cv", "language", "get_score_badge", "created_at")
    list_filter = ("language", "posting__decision", "created_at")
    search_fields = ("cover_letter", "cv__full_name", "posting__raw_text")
    readonly_fields = ("created_at", "updated_at", "preview_cover_letter", "preview_cv_sections")
    date_hierarchy = "created_at"
    
    def get_posting_preview(self, obj):
        """İlan metninin kısa önizlemesi"""
        text = obj.posting.raw_text[:60] + "..." if len(obj.posting.raw_text) > 60 else obj.posting.raw_text
        return text
    get_posting_preview.short_description = "İlan Özeti"
    
    def get_score_badge(self, obj):
        """Eşleşme skorunu renkli badge olarak göster"""
        score = obj.posting.match_score
        if score is None:
            return "-"
        
        if score >= 80:
            color = "green"
        elif score >= 50:
            color = "orange"
        else:
            color = "red"
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color, score
        )
    get_score_badge.short_description = "Score"
    
    def preview_cover_letter(self, obj):
        """Anschreiben önizlemesi"""
        return format_html('<pre style="white-space: pre-wrap;">{}</pre>', obj.cover_letter[:500] + "...")
    preview_cover_letter.short_description = "Anschreiben Vorschau"
    
    def preview_cv_sections(self, obj):
        """CV sections önizlemesi"""
        import json
        return format_html('<pre>{}</pre>', json.dumps(obj.cv_sections, indent=2, ensure_ascii=False)[:500])
    preview_cv_sections.short_description = "CV Sections"