from django.db import models
from cv_manager.models import CV
from job_analyzer.models import JobPosting

# Create your models here.

class ExtractionSnapshot(models.Model):
    KIND_CHOICES = [
        ("POSTING", "posting"),
        ("CV", "cv"),
    ]
    STATUS_CHOICES = [
        ("OK", "ok"),
        ("ERR", "error"),
    ]

    kind = models.CharField(max_length=16, choices=KIND_CHOICES)
    posting = models.ForeignKey(
        JobPosting, null=True, blank=True, on_delete=models.CASCADE, related_name="extraction_snapshots"
    )
    cv = models.ForeignKey(
        CV, null=True, blank=True, on_delete=models.CASCADE, related_name="extraction_snapshots"
    )

    # Ham giriş ve AI çıktısı
    input_text = models.TextField(blank=True)
    output = models.JSONField(default=dict, blank=True)

    # Sağlayıcı meta
    provider = models.CharField(max_length=64, default="stub")
    model_name = models.CharField(max_length=64, blank=True)
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default="OK")
    error_message = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        ref = self.posting_id or self.cv_id or "-" # type: ignore
        return f"{self.kind} snapshot #{self.id} for {ref}" # type: ignore

class CVSource(models.Model):
    """
    Ham CV metni (PDF’ten kopyalanmış düz metin olabilir).
    Aynı CV’ye birden fazla varyasyon eklenebilir.
    """
    cv = models.ForeignKey(CV, on_delete=models.CASCADE, related_name="sources")
    raw_text = models.TextField()
    note = models.CharField(max_length=120, blank=True)  # örn: "IT CV v1", "BWL CV v2"
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"CVSource #{self.id} for CV {self.cv_id}" # type: ignore