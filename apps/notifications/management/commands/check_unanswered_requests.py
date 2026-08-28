from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.bookings.models import BookingRequest
from apps.notifications.models import Notification

UNANSWERED_THRESHOLD_MINUTES = 60


class Command(BaseCommand):
    help = (
        "Find BookingRequests with no first_response_at older than "
        f"{UNANSWERED_THRESHOLD_MINUTES} minutes and queue a reminder Notification. "
        "Run every 15 minutes via cron. Response time is the key business metric (CLAUDE.md §1)."
    )

    def handle(self, *args, **options):
        cutoff = timezone.now() - timezone.timedelta(minutes=UNANSWERED_THRESHOLD_MINUTES)
        stale = BookingRequest.objects.filter(
            first_response_at__isnull=True,
            created_at__lte=cutoff,
            status=BookingRequest.Status.NEW,
        )

        created = 0
        for booking in stale:
            # Avoid spamming: only queue a reminder if we haven't already
            # queued one for this booking in the last hour.
            already_queued = Notification.objects.filter(
                kind=Notification.Kind.UNANSWERED_REMINDER,
                payload__ref_code=booking.ref_code,
                created_at__gte=cutoff,
            ).exists()
            if already_queued:
                continue

            minutes_waiting = int((timezone.now() - booking.created_at).total_seconds() // 60)
            Notification.objects.create(
                kind=Notification.Kind.UNANSWERED_REMINDER,
                payload={
                    "audience": "reminders",
                    "ref_code": booking.ref_code,
                    "text": (
                        f"⏰ Still unanswered: #{booking.ref_code} — {booking.full_name} "
                        f"has waited {minutes_waiting} min with no response!"
                    ),
                },
            )
            created += 1

        self.stdout.write(self.style.SUCCESS(f"Queued {created} unanswered-request reminder(s)."))
