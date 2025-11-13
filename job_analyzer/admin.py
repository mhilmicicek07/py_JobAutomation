from django.contrib import admin, messages
from .models import JobPosting
from . import services
from ai_bridge.models import ExtractionSnapshot
from applicant_letters.models import ApplicationDraft
from applicant_letters import services as letter_services


@admin.action(description="İlanı analiz et ve puanla")
def analyze_postings(modeladmin, request, queryset):
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

    messages.success(request, f"{ok} ilan analiz edildi ve puanlandı.")


@admin.action(description="Taslak oluştur (CV bölümleri + Anschreiben)")
def create_application_drafts(modeladmin, request, queryset):
    created = 0
    for obj in queryset:
        # İlanın hedef alanına göre uygun CV'yi seç
        cv = services.get_primary_cv_or_fallback(obj.target_field)

        # CV bölümlerini ve Anschreiben taslağını üret
        cv_sections = letter_services.build_cv_sections(cv, obj)
        cover_letter = letter_services.build_cover_letter(cv, obj, cv_sections) # type: ignore

        # Aynı ilan + aynı CV için tek taslak (update_or_create ile)
        draft, was_created = ApplicationDraft.objects.update_or_create(
            posting=obj,
            cv=cv,
            defaults={
                "cv_sections": cv_sections,
                "cover_letter": cover_letter,
                "language": "de",
            },
        )
        if was_created:
            created += 1

    messages.success(request, f"{created} ilan için başvuru taslağı oluşturuldu.")


@admin.action(description="AI: İlandan gereksinimleri çıkar (snapshot kaydet)")
def ai_snapshot_postings(modeladmin, request, queryset):
    from ai_bridge import services as ai_services

    ok = 0
    for obj in queryset:
        try:
            output = ai_services.ai_extract_posting(obj)
            ExtractionSnapshot.objects.create(
                kind="POSTING",
                posting=obj,
                input_text=obj.raw_text,
                output=output,
                provider="stub",
                model_name="",
                status="OK",
                error_message="",
            )
            ok += 1
        except Exception as e:  # çok nadir: parsing ya da başka hata
            ExtractionSnapshot.objects.create(
                kind="POSTING",
                posting=obj,
                input_text=obj.raw_text,
                output={},
                provider="stub",
                model_name="",
                status="ERR",
                error_message=str(e),
            )

    messages.success(request, f"{ok} ilan için AI snapshot oluşturuldu.")


@admin.action(description="AI: Son ilan snapshot’ını uygula (skills + experience)")
def apply_latest_posting_snapshot(modeladmin, request, queryset):
    """
    En son (status=OK) POSTING snapshot'ını bulur,
    JobPosting.extracted_skills / extracted_experience + match_score + decision alanlarını günceller.
    """
    applied = 0
    missing = 0

    for obj in queryset:
        snap = (
            ExtractionSnapshot.objects.filter(
                kind="POSTING", posting=obj, status="OK"
            )
            .order_by("-created_at")
            .first()
        )
        if not snap or not snap.output:
            missing += 1
            continue

        data = snap.output or {}
        skills = data.get("skills") or []
        experience = data.get("experience") or []

        obj.extracted_skills = skills
        obj.extracted_experience = experience

        # Snapshot'tan gelen skillerle skoru yeniden hesapla
        cv = services.get_primary_cv_or_fallback(obj.target_field)
        score = services.score_posting_against_cv(cv, skills)
        obj.match_score = score
        obj.decision = services.decision_from_score(score)

        obj.save(
            update_fields=[
                "extracted_skills",
                "extracted_experience",
                "match_score",
                "decision",
                "updated_at",
            ]
        )
        applied += 1

    if applied:
        extra = f" {missing} ilan için snapshot bulunamadı." if missing else ""
        messages.success(
            request,
            f"{applied} ilan için son AI snapshot'ı uygulandı." + extra,
        )
    else:
        messages.warning(request, "Hiçbir ilan için snapshot uygulanamadı.")


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ("id", "target_field", "match_score", "decision", "created_at")
    list_filter = ("target_field", "decision")
    search_fields = ("raw_text",)
    readonly_fields = ("created_at", "updated_at")
    actions = [
        analyze_postings,
        create_application_drafts,
        ai_snapshot_postings,
        apply_latest_posting_snapshot,
    ]