from django.db import models
from cv_manager.models import CV
from job_analyzer.models import JobPosting

# Create your models here.
class ApplicationDraft(models.Model):
    posting = models.ForeignKey(
        JobPosting, on_delete=models.CASCADE, related_name="drafts"
    )
    cv = models.ForeignKey(
        CV, on_delete=models.CASCADE, related_name="drafts"
    )

    # ATS uyumlu kopyalanabilir CV bölümleri (Almanca metin blokları)
    # Örn: {"profil": "...", "kenntnisse": "...", "erfahrung": "..."}
    cv_sections = models.JSONField(default=dict, blank=True)

    # Almanca Anschreiben metni
    cover_letter = models.TextField(blank=True)

    language = models.CharField(max_length=5, default="de")  # "de", "en", "tr" gibi
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            # Aynı ilan + aynı CV için tek taslak tut (sonra istersen kaldırabiliriz)
            models.UniqueConstraint(
                fields=["posting", "cv"],
                name="unique_draft_per_posting_cv",
            )
        ]

    def __str__(self) -> str:
        return f"Draft p{self.posting_id} / cv{self.cv_id} [{self.language}]" # type: ignore[attr-defined]