"""
Soft availability logic (CLAUDE.md §10).

We do NOT hard-block dates — this is a request-based business and the fleet
grows over time. Instead we compare confirmed demand against fleet capacity
for a given date and surface a "Limited availability" signal both on the
site and in the Telegram notification, so a human can make the final call.
BlackoutDate is the only thing that represents a genuinely unavailable day.
"""

from __future__ import annotations

from datetime import date

from apps.bookings.models import BookingRequest
from apps.catalog.models import BlackoutDate, Vehicle


def active_vehicle_count() -> int:
    return Vehicle.objects.filter(is_active=True).count()


def confirmed_requests_for_date(check_date: date):
    """CONFIRMED requests whose [start_date, end_date] span `check_date`."""
    return BookingRequest.objects.filter(
        status=BookingRequest.Status.CONFIRMED,
        start_date__lte=check_date,
        end_date__gte=check_date,
    )


def is_limited_availability(check_date: date) -> bool:
    """True when confirmed demand meets or exceeds active fleet capacity."""
    fleet_size = active_vehicle_count()
    if fleet_size == 0:
        return False
    booked = confirmed_requests_for_date(check_date).count()
    return booked >= fleet_size


def is_blackout(check_date: date, vehicle: Vehicle | None = None) -> bool:
    """True if `check_date` is blacked out fleet-wide, or for `vehicle` specifically."""
    qs = BlackoutDate.objects.filter(date=check_date)
    if vehicle is not None:
        qs = qs.filter(models_q_vehicle_or_null(vehicle))
    else:
        qs = qs.filter(vehicle__isnull=True)
    return qs.exists()


def models_q_vehicle_or_null(vehicle: Vehicle):
    from django.db.models import Q

    return Q(vehicle=vehicle) | Q(vehicle__isnull=True)


def availability_summary(check_date: date) -> dict:
    """Structured summary used by both the site badge and the Telegram message.

    e.g. {"limited": True, "booked": 2, "fleet_size": 2, "blackout": False}
    """
    return {
        "limited": is_limited_availability(check_date),
        "booked": confirmed_requests_for_date(check_date).count(),
        "fleet_size": active_vehicle_count(),
        "blackout": is_blackout(check_date),
    }
