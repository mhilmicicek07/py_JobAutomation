from django.urls import path

from .views import dashboard, cv_create


urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("cv/new/", cv_create, name="cv_create"),
]