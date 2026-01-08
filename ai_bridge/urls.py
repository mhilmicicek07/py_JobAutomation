from django.urls import path
from .views import settings_view

app_name = 'ai_bridge'

urlpatterns = [
    # Kullanıcılar /ai/settings/ adresine gidince bu view çalışacak
    path("settings/", settings_view, name="ai_settings"),
]