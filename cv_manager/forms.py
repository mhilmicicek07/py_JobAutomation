from django import forms
from .models import *

# --- Ana CV Formu ---
class CVForm(forms.ModelForm):
    class Meta:
        model = CV
        fields = ["full_name", "email", "field"]
        labels = {
            "full_name": "Voller Name",
            "email": "E-Mail-Adresse",
            "field": "Fachbereich / Fokus",
        }
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

# --- ALT FORMLAR (CV Parçaları İçin) ---

class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = ["title", "company", "start_date", "end_date", "description"]
        labels = {
            "title": "Jobtitel / Position",
            "company": "Arbeitgeber",
            "start_date": "Beginn",
            "end_date": "Ende (Leer lassen für 'Aktuell')",
            "description": "Beschreibung / Aufgaben",
        }
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "company": forms.TextInput(attrs={"class": "form-control"}),
            "start_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "end_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }

class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = ["degree", "institution", "start_date", "end_date", "status"]
        labels = {
            "degree": "Abschluss / Studiengang",
            "institution": "Institution / Universität",
            "start_date": "Beginn",
            "end_date": "Ende",
            "status": "Status",
        }
        widgets = {
            "degree": forms.TextInput(attrs={"class": "form-control"}),
            "institution": forms.TextInput(attrs={"class": "form-control"}),
            "start_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "end_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }

class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ["name", "level"]
        labels = {
            "name": "Skill / Technologie",
            "level": "Niveau",
        }
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "z. B. Python"}),
            "level": forms.Select(attrs={"class": "form-select"}),
        }

class LanguageForm(forms.ModelForm):
    class Meta:
        model = Language
        fields = ["name", "level"]
        labels = {
            "name": "Sprache",
            "level": "Niveau",
        }
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "z. B. Englisch"}),
            "level": forms.Select(attrs={"class": "form-select"}),
        }