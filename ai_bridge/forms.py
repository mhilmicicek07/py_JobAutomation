from django import forms
from django.utils.translation import gettext_lazy as _
from .models import UserAISettings

class AISettingsForm(forms.ModelForm):
    # API-Schlüssel als Passwortfeld (*****) anzeigen
    api_key = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        required=False,
        label="API Key",
        help_text=_("Ihr API-Schlüssel wird verschlüsselt gespeichert. Achten Sie dennoch auf eine sichere Umgebung.")
    )

    class Meta:
        model = UserAISettings
        fields = ["provider", "api_key", "model_name"]
        widgets = {
            "provider": forms.Select(attrs={"class": "form-control"}),
            "model_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "gpt-4o-mini"}),
        }