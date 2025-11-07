from django.db import models

# Create your models here.

FIELD_CHOICES = [
    ("GEN", "Allgemein"),     # tek CV kullananlar için genel
    ("BWL", "BWL"),
    ("WEB", "Webentwickler"),
]

class CV(models.Model):
    full_name = models.CharField(max_length=120)
    field = models.CharField(max_length=3, choices=FIELD_CHOICES, default="GEN")
    is_primary = models.BooleanField(default=False, help_text="Bu alan için ana/master CV")
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    address = models.CharField(max_length=200, blank=True)
    github = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["full_name", "field"]

    def __str__(self):
        return f"{self.full_name} ({self.field})"
    
class Education(models.Model):
    cv = models.ForeignKey(CV, on_delete=models.CASCADE, related_name="educations")
    degree = models.CharField(max_length=120)
    institution = models.CharField(max_length=160)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[("completed", "completed"), ("ongoing", "ongoing")],
        default="completed",
    )

    class Meta:
        ordering = ["-end_date", "-start_date", "institution"]

    def __str__(self):
        return f"{self.degree} @ {self.institution}"
    
class Experience(models.Model):
    cv = models.ForeignKey(CV, on_delete=models.CASCADE, related_name="experiences")
    title = models.CharField(max_length=140)
    company = models.CharField(max_length=160, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)  # None => aktuell
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["-end_date", "-start_date", "company"]

    def __str__(self):
        return f"{self.title} @ {self.company or 'n/a'}"

class Skill(models.Model):
    LEVELS = [
        ("basic", "basic"),
        ("intermediate", "intermediate"),
        ("advanced", "advanced"),
    ]

    cv = models.ForeignKey(CV, on_delete=models.CASCADE, related_name="skills")
    name = models.CharField(max_length=120, db_index=True)
    level = models.CharField(max_length=20, choices=LEVELS, blank=True)

    class Meta:
        ordering = ["name"]
        unique_together = ("cv", "name")

    def __str__(self):
        return self.name
    
class Certification(models.Model):
    cv = models.ForeignKey(CV, on_delete=models.CASCADE, related_name="certifications")
    name = models.CharField(max_length=160)
    issuer = models.CharField(max_length=160, blank=True)
    issue_date = models.DateField(null=True, blank=True)
    expire_date = models.DateField(null=True, blank=True)
    credential_id = models.CharField(max_length=120, blank=True)

    class Meta:
        ordering = ["-issue_date", "name"]

    def __str__(self):
        return self.name