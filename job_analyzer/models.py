from django.db import models

# Create your models here.
TARGET_FIELD_CHOICES = [
    ("GEN", "Allgemein"),
    ("BWL", "BWL"),
    ("WEB", "Webentwickler"),
]
DECISION_CHOICES = [
    ("APPLY", "apply"),
    ("REVIEW", "review"),
    ("SKIP", "skip"),
]

class JobPosting(models.Model):
    raw_text = models.TextField()  # ilan metni (düz metin)
    target_field = models.CharField(max_length=3, choices=TARGET_FIELD_CHOICES, default="GEN")

    extracted_skills = models.JSONField(default=list, blank=True)       # ["Python","Django",...]
    extracted_experience = models.JSONField(default=list, blank=True)   # ["REST API","SQL",...]

    match_score = models.PositiveSmallIntegerField(null=True, blank=True)  # 0-100

    decision = models.CharField(max_length=10, choices=DECISION_CHOICES, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"JobPosting #{self.pk} [{self.target_field}]"