from django.contrib import admin
from .models import CV, Education, Experience, Skill, Certification

# Register your models here.

@admin.register(CV)
class CVAdmin(admin.ModelAdmin):
    list_display = ("full_name", "field", "is_primary", "email", "updated_at")
    list_filter = ("field", "is_primary")
    search_fields = ("full_name", "email", "address", "github")

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ("degree", "institution", "cv", "start_date", "end_date", "status")
    list_filter = ("status", "institution")
    search_fields = ("degree", "institution", "cv__full_name")
    list_select_related = ("cv",)

@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "cv", "start_date", "end_date")
    list_filter = ("company",)
    search_fields = ("title", "company", "cv__full_name")
    list_select_related = ("cv",)

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "cv", "level")
    list_filter = ("level",)
    search_fields = ("name", "cv__full_name")
    list_select_related = ("cv",)

@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ("name", "issuer", "cv", "issue_date", "expire_date")
    list_filter = ("issuer",)
    search_fields = ("name", "issuer", "cv__full_name")
    list_select_related = ("cv",)