from django.contrib import admin
from .models import CV, Education

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