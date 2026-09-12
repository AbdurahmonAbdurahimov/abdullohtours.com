from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse
from unfold.admin import ModelAdmin

from .models import ActiveSession, ExchangeRate, LoginEvent, Review, SiteSettings


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

    def changelist_view(self, request, extra_context=None):
        # Singleton row: skip the changelist entirely and go straight to
        # the edit form (the sidebar "Site settings" link pointed at the
        # changelist, which had nothing clickable to reach the form from).
        settings_obj = SiteSettings.load()
        return redirect(
            reverse(
                "admin:core_sitesettings_change",
                args=[settings_obj.pk],
            )
        )


@admin.register(ExchangeRate)
class ExchangeRateAdmin(ModelAdmin):
    list_display = ("currency", "rate_from_usd", "updated_at")


@admin.register(LoginEvent)
class LoginEventAdmin(ModelAdmin):
    list_display = ("event_type", "user", "username_attempted", "ip_address", "created_at")
    list_filter = ("event_type",)
    search_fields = ("user__username", "username_attempted", "ip_address")
    date_hierarchy = "created_at"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ActiveSession)
class ActiveSessionAdmin(ModelAdmin):
    list_display = ("user", "ip_address", "created_at", "last_seen_at")
    search_fields = ("user__username", "ip_address")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
