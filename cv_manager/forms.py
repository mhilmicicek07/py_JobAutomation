from django import forms
from .models import CV


class CVForm(forms.ModelForm):
    """
    Basit CV formu.
    Şimdilik sadece temel alanlar:
    - isim
    - alan (GEN / BWL / WEB)
    - primary flag
    - iletişim bilgileri
    """

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
