from django.contrib import admin
from .models import ApplicationDraft

# Register your models here.
@admin.register(ApplicationDraft)
class ApplicationDraftAdmin(admin.ModelAdmin):
    list_display = ("id", "posting", "cv", "language", "created_at")
    search_fields = ("cover_letter",)
    readonly_fields = ("created_at", "updated_at")