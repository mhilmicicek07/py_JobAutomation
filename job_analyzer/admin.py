from django.contrib import admin
from .models import JobPosting

# Register your models here.
@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ("id", "target_field", "match_score", "created_at")
    list_filter = ("target_field",)
    search_fields = ("raw_text",)
    readonly_fields = ("created_at", "updated_at")