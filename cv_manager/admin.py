from django.contrib import admin
from .models import *

# CV Modelini Özelleştirilmiş Gösterme
@admin.register(CV)
class CVAdmin(admin.ModelAdmin):
    list_display = ("full_name", "field", "user", "created_at")
    list_filter = ("field", "user")
    search_fields = ("full_name", "email")

@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "cv", "start_date", "end_date")
    list_filter = ("cv",)

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ("degree", "institution", "cv", "status")
    list_filter = ("status", "cv")

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "level", "cv")
    list_filter = ("level", "cv")
    search_fields = ("name",)

# --- YENİ EKLENEN KISIM ---
@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ("name", "level", "cv")
    list_filter = ("level", "cv")
    search_fields = ("name",)
# --------------------------

# Diğer modeller varsa onlar da kalabilir (Certification, Process vb.)
admin.site.register(Certification)
admin.site.register(Process)