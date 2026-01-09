from types import SimpleNamespace
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import *
from ai_bridge.models import CVSource, UserAISettings
from ai_bridge import services as ai_services

# ── MEVCUT VİEW'LAR (DOKUNULMADI) ─────────────────────────────────────────────

@login_required
def dashboard(request):
    cvs = CV.objects.filter(user=request.user).order_by("full_name", "field")

    # AI ayarları kontrolü - eğer ayarlanmadıysa uyarı göster
    try:
        ai_settings = request.user.ai_settings
        if not ai_settings.api_key:
            messages.warning(
                request,
                '⚠️ <strong>AI-Funktionen nicht verfügbar!</strong> '
                'Bitte konfigurieren Sie Ihre AI-Einstellungen unter '
                '<a href="{% url "ai_bridge:ai_settings" %}" class="alert-link">Einstellungen</a>, '
                'um CV-Import und Bewerbungsanalysen zu nutzen.'
            )
    except UserAISettings.DoesNotExist:
        messages.warning(
            request,
            '⚠️ <strong>AI-Funktionen nicht verfügbar!</strong> '
            'Bitte konfigurieren Sie Ihre AI-Einstellungen unter '
            '<a href="{% url "ai_bridge:ai_settings" %}" class="alert-link">Einstellungen</a>, '
            'um CV-Import und Bewerbungsanalysen zu nutzen.'
        )

    return render(request, "cv_manager/dashboard.html", {"cvs": cvs})

@login_required
def cv_create(request):
    if request.method == "POST":
        form = CVForm(request.POST)
        if form.is_valid():
            cv = form.save(commit=False)
            cv.user = request.user
            cv.save()
            # Oluşturduktan sonra detay sayfasına yönlendir
            return redirect("cv_manager:cv_detail", pk=cv.pk)
    else:
        form = CVForm()
    return render(request, "cv_manager/cv_form.html", {"form": form})

@login_required
def cv_update(request, pk):
    """Ana başlık bilgilerini düzenler (İsim, Alan vs.)"""
    cv = get_object_or_404(CV, pk=pk, user=request.user)
    if request.method == "POST":
        form = CVForm(request.POST, instance=cv)
        if form.is_valid():
            form.save()
            return redirect("cv_manager:cv_detail", pk=cv.pk)
    else:
        form = CVForm(instance=cv)
    return render(request, "cv_manager/cv_form.html", {"form": form, "cv": cv})

@login_required
def cv_import(request, pk):
    cv = get_object_or_404(CV, pk=pk, user=request.user)
    if request.method == "POST":
        form = CVImportForm(request.POST)
        if form.is_valid():
            raw_text = form.cleaned_data["raw_text"]
            note = form.cleaned_data["note"]
            source = CVSource.objects.create(cv=cv, raw_text=raw_text, note=note)

            data = ai_services.ai_extract_cv(source, user=request.user)
            snapshot = SimpleNamespace(output=data)
            stats = ai_services.apply_cv_snapshot(cv, snapshot)

            messages.success(request, f"AI-Import fertig: {stats.get('skills',0)} Skills.")
            return redirect("cv_manager:cv_detail", pk=cv.pk)
    else:
        form = CVImportForm()
    return render(request, "cv_manager/cv_import.html", {"form": form, "cv": cv})

@login_required
def cv_delete(request, pk):
    cv = get_object_or_404(CV, pk=pk, user=request.user)
    if request.method == "POST":
        cv.delete()
        messages.success(request, f"CV '{cv.full_name}' gelöscht.")
        return redirect("cv_manager:dashboard")
    return render(request, "cv_manager/cv_delete_confirm.html", {"cv": cv})


# ── YENİ: CV DETAY VE YÖNETİM (CV STUDIO) ─────────────────────────────────────

@login_required
def cv_detail(request, pk):
    """
    CV'nin tüm parçalarını gösteren ve yöneten ana ekran.
    """
    cv = get_object_or_404(CV, pk=pk, user=request.user)
    
    context = {
        "cv": cv,
        "experiences": cv.experiences.all().order_by("-end_date", "-start_date"), # type: ignore
        "educations": cv.educations.all().order_by("-end_date", "-start_date"), # type: ignore
        "skills": cv.skills.all().order_by("name"), # type: ignore
        "languages": cv.languages.all(),  # YENİ EKLENEN SATIR # type: ignore
    }
    return render(request, "cv_manager/cv_detail.html", context)


# ── EXPERIENCE CRUD ───────────────────────────────────────────────────────────

@login_required
def add_experience(request, cv_id):
    cv = get_object_or_404(CV, pk=cv_id, user=request.user)
    if request.method == "POST":
        form = ExperienceForm(request.POST)
        if form.is_valid():
            exp = form.save(commit=False)
            exp.cv = cv
            exp.save()
            messages.success(request, "Berufserfahrung hinzugefügt.")
            return redirect("cv_manager:cv_detail", pk=cv.pk)
    else:
        form = ExperienceForm()
    return render(request, "cv_manager/item_form.html", {"form": form, "title": "Erfahrung hinzufügen"})

@login_required
def edit_experience(request, cv_id, exp_id):
    cv = get_object_or_404(CV, pk=cv_id, user=request.user)
    exp = get_object_or_404(Experience, pk=exp_id, cv=cv)
    if request.method == "POST":
        form = ExperienceForm(request.POST, instance=exp)
        if form.is_valid():
            form.save()
            messages.success(request, "Berufserfahrung aktualisiert.")
            return redirect("cv_manager:cv_detail", pk=cv.pk)
    else:
        form = ExperienceForm(instance=exp)
    return render(request, "cv_manager/item_form.html", {"form": form, "title": "Erfahrung bearbeiten"})

@login_required
def delete_experience(request, cv_id, exp_id):
    cv = get_object_or_404(CV, pk=cv_id, user=request.user)
    exp = get_object_or_404(Experience, pk=exp_id, cv=cv)
    if request.method == "POST":
        exp.delete()
        messages.success(request, "Eintrag gelöscht.")
    return redirect("cv_detail", pk=cv.pk)


# ── EDUCATION CRUD ────────────────────────────────────────────────────────────

@login_required
def add_education(request, cv_id):
    cv = get_object_or_404(CV, pk=cv_id, user=request.user)
    if request.method == "POST":
        form = EducationForm(request.POST)
        if form.is_valid():
            edu = form.save(commit=False)
            edu.cv = cv
            edu.save()
            messages.success(request, "Ausbildung hinzugefügt.")
            return redirect("cv_manager:cv_detail", pk=cv.pk)
    else:
        form = EducationForm()
    return render(request, "cv_manager/item_form.html", {"form": form, "title": "Ausbildung hinzufügen"})

@login_required
def edit_education(request, cv_id, edu_id):
    cv = get_object_or_404(CV, pk=cv_id, user=request.user)
    edu = get_object_or_404(Education, pk=edu_id, cv=cv)
    if request.method == "POST":
        form = EducationForm(request.POST, instance=edu)
        if form.is_valid():
            form.save()
            messages.success(request, "Ausbildung aktualisiert.")
            return redirect("cv_manager:cv_detail", pk=cv.pk)
    else:
        form = EducationForm(instance=edu)
    return render(request, "cv_manager/item_form.html", {"form": form, "title": "Ausbildung bearbeiten"})

@login_required
def delete_education(request, cv_id, edu_id):
    cv = get_object_or_404(CV, pk=cv_id, user=request.user)
    edu = get_object_or_404(Education, pk=edu_id, cv=cv)
    if request.method == "POST":
        edu.delete()
        messages.success(request, "Eintrag gelöscht.")
    return redirect("cv_detail", pk=cv.pk)


# ── SKILL CRUD ────────────────────────────────────────────────────────────────

@login_required
def add_skill(request, cv_id):
    cv = get_object_or_404(CV, pk=cv_id, user=request.user)
    if request.method == "POST":
        form = SkillForm(request.POST)
        if form.is_valid():
            # Skill zaten varsa hata vermemesi için get_or_create mantığı veya try-catch
            try:
                skill = form.save(commit=False)
                skill.cv = cv
                skill.save()
                messages.success(request, f"Skill '{skill.name}' hinzugefügt.")
            except Exception:
                messages.warning(request, "Dieser Skill existiert bereits.")
            return redirect("cv_manager:cv_detail", pk=cv.pk)
    return redirect("cv_detail", pk=cv.pk)

@login_required
def delete_skill(request, cv_id, skill_id):
    cv = get_object_or_404(CV, pk=cv_id, user=request.user)
    skill = get_object_or_404(Skill, pk=skill_id, cv=cv)
    if request.method == "POST":
        skill.delete()
        messages.success(request, "Skill gelöscht.")
    return redirect("cv_detail", pk=cv.pk)

# ── LANGUAGE CRUD ─────────────────────────────────────────────────────────────

@login_required
def add_language(request, cv_id):
    cv = get_object_or_404(CV, pk=cv_id, user=request.user)
    if request.method == "POST":
        form = LanguageForm(request.POST)
        if form.is_valid():
            lang = form.save(commit=False)
            lang.cv = cv
            lang.save()
            messages.success(request, f"Sprache '{lang.name}' hinzugefügt.")
            return redirect("cv_manager:cv_detail", pk=cv.pk)
    return redirect("cv_detail", pk=cv.pk)

@login_required
def delete_language(request, cv_id, lang_id):
    cv = get_object_or_404(CV, pk=cv_id, user=request.user)
    lang = get_object_or_404(Language, pk=lang_id, cv=cv)
    if request.method == "POST":
        lang.delete()
        messages.success(request, "Sprache gelöscht.")
    return redirect("cv_detail", pk=cv.pk)