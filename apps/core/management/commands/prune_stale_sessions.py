from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.core.models import ActiveSession


class Command(BaseCommand):
    help = (
        "Delete ActiveSession rows whose browser session has expired "
        "(closed without logging out, so no logout signal ever fired). "
        "Run periodically via cron — see apps.core.models.ActiveSession."
    )

    def handle(self, *args, **options):
        cutoff = timezone.now() - timezone.timedelta(seconds=settings.SESSION_COOKIE_AGE)
        deleted, _ = ActiveSession.objects.filter(last_seen_at__lt=cutoff).delete()
        self.stdout.write(self.style.SUCCESS(f"Pruned {deleted} stale active session(s)."))
