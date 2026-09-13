from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from .models import UserAISettings
from .forms import AISettingsForm

# Create your views here.

@login_required
def settings_view(request):
    """
    Verwaltet die KI-Anbieter- und API-Schlüssel-Einstellungen des Benutzers.
    """
    # Einstellungen des Benutzers laden, ggf. neu anlegen (get_or_create)
    user_settings, created = UserAISettings.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = AISettingsForm(request.POST, instance=user_settings)
        if form.is_valid():
            form.save()
            messages.success(request, _("Ihre AI-Einstellungen wurden erfolgreich gespeichert."))
            # Nach dem Speichern auf dieselbe Seite umleiten (PRG-Muster)
            return redirect("ai_bridge:ai_settings")
    else:
        form = AISettingsForm(instance=user_settings)

    return render(request, "ai_bridge/settings.html", {"form": form})