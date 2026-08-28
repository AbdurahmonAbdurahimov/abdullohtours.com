from django.core.management.base import BaseCommand

from apps.notifications.models import Notification
from apps.notifications.senders import send_notification


class Command(BaseCommand):
    help = "Send all PENDING (and previously FAILED) Notification rows. Run every minute via cron."

    def handle(self, *args, **options):
        qs = Notification.objects.filter(
            status__in=[Notification.Status.PENDING, Notification.Status.FAILED]
        )
        sent = 0
        failed = 0
        for notification in qs:
            if send_notification(notification):
                sent += 1
            else:
                failed += 1
        self.stdout.write(self.style.SUCCESS(f"Sent {sent} notification(s), {failed} failed."))
