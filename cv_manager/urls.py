from django.urls import path
from .views import *

urlpatterns = [
    # Ana İşlemler
    path("", dashboard, name="dashboard"),
    path("create/", cv_create, name="cv_create"),
    path("<int:pk>/update/", cv_update, name="cv_update"), # Sadece başlık/email düzenler
    path("<int:pk>/delete/", cv_delete, name="cv_delete"),
    path("<int:pk>/import/", cv_import, name="cv_import"),

    # YENİ: Detay Sayfası (CV Studio)
    path("<int:pk>/manage/", cv_detail, name="cv_detail"),

    # YENİ: Experience (Deneyim) İşlemleri
    path("<int:cv_id>/experience/add/", add_experience, name="add_experience"),
    path("<int:cv_id>/experience/<int:exp_id>/edit/", edit_experience, name="edit_experience"),
    path("<int:cv_id>/experience/<int:exp_id>/delete/", delete_experience, name="delete_experience"),

    # YENİ: Education (Eğitim) İşlemleri
    path("<int:cv_id>/education/add/", add_education, name="add_education"),
    path("<int:cv_id>/education/<int:edu_id>/edit/", edit_education, name="edit_education"),
    path("<int:cv_id>/education/<int:edu_id>/delete/", delete_education, name="delete_education"),

    # YENİ: Skill (Yetenek) İşlemleri
    path("<int:cv_id>/skill/add/", add_skill, name="add_skill"),
    path("<int:cv_id>/skill/<int:skill_id>/delete/", delete_skill, name="delete_skill"),
]