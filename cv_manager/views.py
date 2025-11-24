from django.shortcuts import render
from .models import CV

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