from django.urls import path
from .views import settings_view

urlpatterns = [
    # Kullanıcılar /ai/settings/ adresine gidince bu view çalışacak
    path("settings/", settings_view, name="ai_settings"),
]