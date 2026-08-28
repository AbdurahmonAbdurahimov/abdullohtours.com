from django.db import models


class Notification(models.Model):
    """Every outbound message (Telegram or otherwise) is written here FIRST,
    then sent (CLAUDE.md §8): "A notification must never be lost because the
    Telegram API was briefly down." Failures stay PENDING/FAILED and are
    retried by cron (send_pending_notifications) — never deleted.
    """

    class Kind(models.TextChoices):
        NEW_BOOKING = "NEW_BOOKING", "New booking request"
        UNANSWERED_REMINDER = "UNANSWERED_REMINDER", "Unanswered request reminder"
        DB_BACKUP = "DB_BACKUP", "Database backup document"
        STATUS_UPDATE = "STATUS_UPDATE", "Booking status update"
        OTHER = "OTHER", "Other"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SENT = "SENT", "Sent"
        FAILED = "FAILED", "Failed"

    kind = models.CharField(max_length=32, choices=Kind.choices)
    payload = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    attempts = models.PositiveIntegerField(default=0)
    last_error = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.kind} [{self.status}] #{self.pk}"


class TelegramAdmin(models.Model):
    chat_id = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    receives_bookings = models.BooleanField(default=True)
    receives_reminders = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Telegram admin"
        verbose_name_plural = "Telegram admins"

    def __str__(self) -> str:
        return self.name or self.chat_id
