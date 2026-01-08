from django.urls import path

from .views import *

app_name = 'job_analyzer'

urlpatterns = [
    path("quick-apply/", quick_apply, name="quick_apply"),
    path("history/", application_history, name="application_history"),
    path("history/<int:pk>/", application_detail, name="application_detail"),
]