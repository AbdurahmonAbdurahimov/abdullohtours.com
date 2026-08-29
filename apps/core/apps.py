from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
    verbose_name = "Core"

    def ready(self):
        from django.db.models.signals import post_delete

        from .signals import cleanup_webp_images_on_delete

        post_delete.connect(cleanup_webp_images_on_delete)
