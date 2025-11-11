from django.contrib import admin, messages
from .models import ExtractionSnapshot, CVSource
from . import services

# Register your models here.

@admin.register(ExtractionSnapshot)
class ExtractionSnapshotAdmin(admin.ModelAdmin):
    list_display = ("id", "kind", "cv", "posting", "provider", "status", "created_at")
    list_filter = ("kind", "provider", "status")
    search_fields = ("input_text",)
    readonly_fields = ("created_at",)


@admin.action(description="AI: CV’den çıkar (snapshot kaydet)")
def ai_extract_and_snapshot(modeladmin, request, queryset):
    ok = 0
    for src in queryset:
        try:
            out = services.ai_extract_cv(src)
            ExtractionSnapshot.objects.create(
                kind="CV",
                cv=src.cv,
                input_text=src.raw_text or "",
                output=out,
                provider="stub",
                model_name="",
                status="OK",
                error_message="",
            )
            ok += 1
        except Exception as e:
            ExtractionSnapshot.objects.create(
                kind="CV",
                cv=src.cv,
                input_text=src.raw_text or "",
                output={},
                provider="stub",
                model_name="",
                status="ERR",
                error_message=str(e),
            )
    messages.success(request, f"{ok} kaynak için CV snapshot’ı oluşturuldu.")


@admin.action(description="AI: Son CV snapshot’ını uygula (merge)")
def apply_latest_cv_snapshot(modeladmin, request, queryset):
    ok = 0
    for src in queryset:
        snap = ExtractionSnapshot.objects.filter(kind="CV", cv=src.cv).order_by("-created_at").first()
        if not snap or not snap.output:
            continue
        stats = services.apply_cv_snapshot(src.cv, snap.output, merge=True)
        ok += 1
    messages.success(request, f"{ok} kaynak için snapshot uygulandı (merge).")


@admin.register(CVSource)
class CVSourceAdmin(admin.ModelAdmin):
    list_display = ("id", "cv", "note", "created_at")
    search_fields = ("raw_text", "note")
    readonly_fields = ("created_at",)
    actions = [ai_extract_and_snapshot, apply_latest_cv_snapshot]