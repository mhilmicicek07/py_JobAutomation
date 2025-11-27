from django.urls import path

from .views import *

urlpatterns = [
    path("quick-apply/", quick_apply, name="quick_apply"),
]