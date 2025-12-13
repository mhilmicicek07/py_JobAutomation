from django import forms
from .models import CV

class CVForm(forms.ModelForm):
    class Meta:
        model = CV
        fields = ["full_name", "email", "field"]
        labels = {
            "full_name": "Voller Name",
            "email": "E-Mail-Adresse",
            "field": "Fachbereich / Fokus",
        }
        # Bootstrap stilleri için widget tanımları
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "z. B. Max Mustermann"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "name@example.com"}),
            "field": forms.Select(attrs={"class": "form-select"}),
        }

class CVImportForm(forms.Form):
    raw_text = forms.CharField(
        label="CV-Text (Copy & Paste)",
        widget=forms.Textarea(attrs={
            "class": "form-control", 
            "rows": 10, 
            "placeholder": "Kopieren Sie hier den gesamten Text Ihres Lebenslaufs hinein (z. B. aus einem PDF)."
        }),
        help_text="Fügen Sie den Text einfach ein. Die KI wird versuchen, Struktur daraus zu lesen."
    )
    note = forms.CharField(
        label="Notiz (Optional)",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "z. B. LinkedIn Profil Version"}),
    )