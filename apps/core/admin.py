from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import ExchangeRate, SiteSettings

# NOTE: the full custom dashboard (today's requests / pending count /
# confirmed this month / estimated revenue / recent requests / abandoned
# builders, per CLAUDE.md §11) is follow-up work, not part of this scaffold
# pass. This registers SiteSettings so it's editable now.


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
