from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserAISettings
from .forms import AISettingsForm

# Create your views here.

@login_required
def settings_view(request):
    """
    Kullanıcının AI sağlayıcı ve API anahtarı ayarlarını yönetmesini sağlar.
    """
    # Kullanıcının ayarını getir, yoksa oluştur (get_or_create)
    user_settings, created = UserAISettings.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = AISettingsForm(request.POST, instance=user_settings)
        if form.is_valid():
            form.save()
            messages.success(request, "AI Ayarlarınız başarıyla kaydedildi.")
            # Formu kaydettikten sonra aynı sayfaya yönlendir (PRG pattern)
            return redirect("ai_bridge:ai_settings")
    else:
        form = AISettingsForm(instance=user_settings)

    return render(request, "ai_bridge/settings.html", {"form": form})