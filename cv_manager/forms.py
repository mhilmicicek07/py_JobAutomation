from django import forms

from .models import CV


class CVForm(forms.ModelForm):
    class Meta:
        model = CV
        fields = [
            "full_name",
            "field",
            "is_primary",
            "email",
            "phone",
            "address",
            "github",
        ]


class CVImportForm(forms.Form):
    raw_text = forms.CharField(
        label="CV-Text (vollständig)",
        widget=forms.Textarea(attrs={"rows": 20}),
        help_text="Gesamten CV-Text aus PDF/Word hier einfügen.",
    )
    note = forms.CharField(
        label="Notiz",
        max_length=120,
        required=False,
    )
