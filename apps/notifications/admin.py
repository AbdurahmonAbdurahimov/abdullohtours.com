from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Notification, TelegramAdmin


@admin.register(Notification)
class NotificationAdmin(ModelAdmin):
    list_display = ("kind", "status", "attempts", "created_at", "sent_at")
    list_filter = ("kind", "status")
    readonly_fields = ("created_at",)


@admin.register(TelegramAdmin)
class TelegramAdminAdmin(ModelAdmin):
    list_display = ("name", "chat_id", "is_active", "receives_bookings", "receives_reminders")
    list_filter = ("is_active", "receives_bookings", "receives_reminders")
    search_fields = ("name", "chat_id")
