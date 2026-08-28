from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import ExchangeRate, Review, SiteSettings


@admin.register(Review)
class ReviewAdmin(ModelAdmin):
    list_display = (
        "author_name",
        "rating",
        "source",
        "package",
        "destination",
        "is_published",
        "created_at",
    )
    list_filter = ("is_published", "source", "rating")
    search_fields = ("author_name", "body")
    autocomplete_fields = ("package", "destination")


@admin.register(SiteSettings)
class SiteSettingsAdmin(ModelAdmin):
    list_display = ("__str__", "phone", "whatsapp_number", "email")

    def has_add_permission(self, request):
        # Singleton — only the seeded row should ever exist.
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ExchangeRate)
class ExchangeRateAdmin(ModelAdmin):
    list_display = ("currency", "rate_from_usd", "updated_at")
