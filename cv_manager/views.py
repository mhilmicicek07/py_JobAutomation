from types import SimpleNamespace
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import CV
from .forms import CVForm, CVImportForm
from ai_bridge.models import CVSource
from ai_bridge import services as ai_services

@login_required
def dashboard(request):
    """
    Kullanıcının kendi CV'lerini listeler.
    """
    # SADECE giriş yapan kullanıcının CV'leri (user=request.user)
    cvs = CV.objects.filter(user=request.user).order_by("full_name", "field")
    return render(request, "cv_manager/dashboard.html", {"cvs": cvs})

@login_required
def cv_create(request):
    """
    Yeni CV oluşturur ve sahibini (user) giriş yapan kişi yapar.
    """
    if request.method == "POST":
        form = CVForm(request.POST)
        if form.is_valid():
            cv = form.save(commit=False) # Veritabanına henüz yazma
            cv.user = request.user       # Sahibini ata
            cv.save()                    # Şimdi yaz
            return redirect("dashboard")
    else:
        form = CVForm()
    return render(request, "cv_manager/cv_form.html", {"form": form})

@login_required
def cv_update(request, pk):
    """
    Mevcut CV'yi günceller.
    Başkasının CV'sine erişimi engellemek için user=request.user şartı var.
    """
    cv = get_object_or_404(CV, pk=pk, user=request.user)
    
    if request.method == "POST":
        form = CVForm(request.POST, instance=cv)
        if form.is_valid():
            form.save()
            return redirect("dashboard")
    else:
        form = CVForm(instance=cv)
    return render(request, "cv_manager/cv_form.html", {"form": form, "cv": cv})

@login_required
def cv_import(request, pk):
    """
    CV metnini AI ile analiz eder ve veritabanına ekler.
    """
    cv = get_object_or_404(CV, pk=pk, user=request.user)

    if request.method == "POST":
        form = CVImportForm(request.POST)
        if form.is_valid():
            raw_text = form.cleaned_data["raw_text"]
            note = form.cleaned_data["note"]

            source = CVSource.objects.create(
                cv=cv,
                raw_text=raw_text,
                note=note,
            )

            # AI Servisini çağır (Kullanıcı context'i ile)
            data = ai_services.ai_extract_cv(source, user=request.user)

            # Gelen veriyi (JSON) veritabanına uygula (Skill, Experience vb.)
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

    return render(request, "cv_manager/cv_import.html", {"form": form, "cv": cv})

@login_required
def cv_delete(request, pk):
    """
    CV'yi siler.
    """
    cv = get_object_or_404(CV, pk=pk, user=request.user)
    
    if request.method == "POST":
        cv.delete()
        messages.success(request, f"CV '{cv.full_name}' silindi.")
        return redirect("dashboard")
    return render(request, "cv_manager/cv_delete_confirm.html", {"cv": cv})