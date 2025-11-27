from types import SimpleNamespace

from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from .models import CV
from .forms import CVForm, CVImportForm

from ai_bridge.models import CVSource
from ai_bridge import services as ai_services


def dashboard(request):
    cvs = CV.objects.all().order_by("full_name", "field")
    return render(request, "cv_manager/dashboard.html", {"cvs": cvs})


def cv_create(request):
    if request.method == "POST":
        form = CVForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("dashboard")
    else:
        form = CVForm()

    return render(request, "cv_manager/cv_form.html", {"form": form})


def cv_update(request, pk):
    cv = get_object_or_404(CV, pk=pk)

    if request.method == "POST":
        form = CVForm(request.POST, instance=cv)
        if form.is_valid():
            form.save()
            return redirect("dashboard")
    else:
        form = CVForm(instance=cv)

    return render(request, "cv_manager/cv_form.html", {"form": form, "cv": cv})


def cv_import(request, pk):
    """
    Belirli bir CV için:
    - ham CV metni al
    - CVSource kaydı oluştur
    - AI ile parse et
    - sonucu Skill / Experience / Education tablolarına uygula
    """
    cv = get_object_or_404(CV, pk=pk)

    if request.method == "POST":
        form = CVImportForm(request.POST)
        if form.is_valid():
            raw_text = form.cleaned_data["raw_text"]
            note = form.cleaned_data["note"]

            # 1) CVSource kaydı
            source = CVSource.objects.create(
                cv=cv,
                raw_text=raw_text,
                note=note,
            )

            # 2) AI ile çıkarım (OpenAI varsa OpenAI, yoksa heuristik)
            data = ai_services.ai_extract_cv(source)

            # 3) Çıkan JSON'u mevcut apply_cv_snapshot mantığıyla uygula
            snapshot = SimpleNamespace(output=data)
            stats = ai_services.apply_cv_snapshot(cv, snapshot)

            messages.success(
                request,
                f"AI-Import fertig: "
                f"{stats.get('skills', 0)} Skills, "
                f"{stats.get('experience', 0)} Erfahrungen, "
                f"{stats.get('education', 0)} Ausbildungen hinzugefügt.",
            )

            return redirect("dashboard")
    else:
        form = CVImportForm()

    return render(
        request,
        "cv_manager/cv_import.html",
        {"form": form, "cv": cv},
    )
