from django.contrib import admin
from .models import CV

# Register your models here.

@admin.register(CV)
class CVAdmin(admin.ModelAdmin):
    list_display = ("full_name", "field", "is_primary", "email", "updated_at")
    list_filter = ("field", "is_primary")
    search_fields = ("full_name", "email", "address", "github")