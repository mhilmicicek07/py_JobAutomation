from django import forms
from .models import UserAISettings

class AISettingsForm(forms.ModelForm):
    # API key'i şifre alanı gibi (*****) göstermek için widget özelleştiriyoruz
    api_key = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        required=False,
        label="API Key",
        help_text="API anahtarınız şifrelenerek saklanmaz, güvenli ortamda tuttuğunuzdan emin olun."
    )

    class Meta:
        model = UserAISettings
        fields = ["provider", "api_key", "model_name"]
        widgets = {
            "provider": forms.Select(attrs={"class": "form-control"}),
            "model_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "gpt-4o-mini"}),
        }