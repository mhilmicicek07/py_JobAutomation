from django.urls import path

from .views import *


urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("cv/new/", cv_create, name="cv_create"),
    path("cv/<int:pk>/edit/", cv_update, name="cv_update"),
    path("cv/<int:pk>/import/", cv_import, name="cv_import"),
]