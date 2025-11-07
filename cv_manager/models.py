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
