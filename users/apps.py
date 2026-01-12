from django.apps import AppConfig
from django.db.models.signals import post_migrate


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "users"

    def ready(self):
        from django.contrib.auth import get_user_model

        def create_demo_user(sender, **kwargs):
            User = get_user_model()

            if not User.objects.filter(username="demo").exists():
                User.objects.create_user(
                    username="demo",
                    email="demo@test.com",
                    password="kullanici123.",
                )

        post_migrate.connect(create_demo_user)