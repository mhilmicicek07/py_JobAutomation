from django.db import models
from django.contrib.auth.models import User
from cv_manager.models import CV
from job_analyzer.models import JobPosting
from .encryption import encrypt_api_key, decrypt_api_key

# ── KULLANICI AYARLARI (YENİ) ─────────────────────────────────────────────────

class UserAISettings(models.Model):
    PROVIDER_CHOICES = [
        ("openai", "OpenAI (GPT-4o, etc.)"),
        ("gemini", "Google Gemini"),
        ("groq", "Groq (Llama3, Mixtral)"),
    ]

    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name="ai_settings"
    )
    provider = models.CharField(
        max_length=20, 
        choices=PROVIDER_CHOICES, 
        default="openai",
        help_text="Kullanmak istediğiniz AI sağlayıcısı."
    )
    api_key = models.CharField(
        max_length=512,  # Şifrelenmiş key daha uzun olabilir
        blank=True, 
        help_text="Seçilen sağlayıcıya ait API Anahtarı (şifrelenmiş olarak saklanır)"
    )
    model_name = models.CharField(
        max_length=50, 
        blank=True, 
        help_text="Özel model adı (Boş bırakılırsa varsayılan kullanılır. Örn: gpt-4o-mini)"
    )

    def save(self, *args, **kwargs):
        """
        API key'i otomatik şifrele.
        """
        if self.api_key and not self._is_encrypted(self.api_key):
            self.api_key = encrypt_api_key(self.api_key)
        super().save(*args, **kwargs)
    
    def get_decrypted_api_key(self) -> str:
        """
        Şifrelenmiş API key'i çözülmüş halde döndür.
        """
        return decrypt_api_key(self.api_key) if self.api_key else ""
    
    @staticmethod
    def _is_encrypted(value: str) -> bool:
        """
        Değerin zaten şifrelenmiş olup olmadığını kontrol et.
        Fernet encrypted strings 'gAAAAA' ile başlar (base64 encoding).
        """
        return value.startswith("gAAAAA") if value else False

    def __str__(self):
        return f"{self.user.username} - {self.provider}"


# ── MEVCUT MODELLER ───────────────────────────────────────────────────────────

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
    raw_text = models.TextField(help_text="CV içeriğini buraya yapıştırın.")
    note = models.CharField(max_length=100, blank=True, help_text="Örn: LinkedIn versiyonu")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Source for {self.cv} ({self.created_at.date()})"