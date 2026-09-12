from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
    verbose_name = "Core"

    def ready(self):
        from django.contrib.auth.signals import (
            user_logged_in,
            user_logged_out,
            user_login_failed,
        )
        from django.db.models.signals import post_delete

        from .signals import (
            cleanup_webp_images_on_delete,
            record_login,
            record_login_failed,
            record_logout,
        )

        post_delete.connect(cleanup_webp_images_on_delete)
        user_logged_in.connect(record_login)
        user_logged_out.connect(record_logout)
        user_login_failed.connect(record_login_failed)
