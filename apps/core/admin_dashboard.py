"""
Custom admin dashboard (CLAUDE.md §11): "today's requests, pending count,
confirmed this month, estimated revenue, recent requests table, abandoned
builders". Wired via UNFOLD["DASHBOARD_CALLBACK"] in config/settings/base.py
— django-unfold calls this with (request, context) on every admin index
render and renders whatever we add here through templates/admin/index.html.
"""

from __future__ import annotations

from django.db.models import Sum
from django.utils import timezone

from apps.bookings.models import BookingRequest, BuilderSession


def dashboard_callback(request, context: dict) -> dict:
    today = timezone.localdate()
    month_start = today.replace(day=1)

    pending = BookingRequest.objects.filter(status=BookingRequest.Status.NEW)
    confirmed_this_month = BookingRequest.objects.filter(
        status=BookingRequest.Status.CONFIRMED, created_at__date__gte=month_start
    )
    revenue_month = confirmed_this_month.aggregate(total=Sum("estimated_total_usd"))["total"] or 0

    recent = BookingRequest.objects.select_related("vehicle_class")[:10]
    recent_requests_table = {
        "headers": ["Ref", "Name", "Status", "Dates", "Est. total", "Created"],
        "rows": [
            [
                booking.ref_code,
                booking.full_name,
                booking.get_status_display(),
                (
                    f"{booking.start_date:%d %b} – {booking.end_date:%d %b %Y}"
                    if booking.start_date and booking.end_date
                    else "—"
                ),
                f"${booking.estimated_total_usd:,.0f}" if booking.estimated_total_usd else "—",
                booking.created_at.strftime("%d %b %Y %H:%M"),
            ]
            for booking in recent
        ],
    }

    context.update(
        {
            "kpi_today": BookingRequest.objects.filter(created_at__date=today).count(),
            "kpi_pending": pending.count(),
            "kpi_confirmed_month": confirmed_this_month.count(),
            "kpi_revenue_month": revenue_month,
            "kpi_abandoned_builders": BuilderSession.objects.filter(is_converted=False).count(),
            "recent_requests_table": recent_requests_table,
        }
    )
    return context
