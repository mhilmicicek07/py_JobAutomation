from django.shortcuts import render, redirect, get_object_or_404

from .models import CV
from .forms import CVForm

# Create your views here.
def dashboard(request):
    """
    Basit CV listesi view'i.
    Şimdilik sadece tüm CV'leri context'e verir.
    Template ve URL yönlendirmesini sonraki adımlarda ekleyeceğiz.
    """
    cvs = CV.objects.all().order_by("full_name", "field")
    context = {
        "cvs": cvs,
    }
    return render(request, "cv_manager/dashboard.html", context)

def cv_create(request):
    """
    Yeni CV oluşturma view'i.
    Şimdilik:
    - GET: boş form
    - POST: form geçerliyse kaydet ve dashboard'a yönlendir
    """
    if request.method == "POST":
        form = CVForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("dashboard")
    else:
        form = CVForm()

    return render(request, "cv_manager/cv_form.html", {"form": form})

def cv_update(request, pk):
    """
    Var olan CV'yi düzenleme view'i.
    - GET: mevcut verilerle form
    - POST: geçerliyse kaydet ve dashboard'a dön
    """
    cv = get_object_or_404(CV, pk=pk)

    if request.method == "POST":
        form = CVForm(request.POST, instance=cv)
        if form.is_valid():
            form.save()
            return redirect("dashboard")
    else:
        form = CVForm(instance=cv)

    return render(request, "cv_manager/cv_form.html", {"form": form, "cv": cv})