import csv

from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display

from .models import BookingItem, BookingRequest, BuilderSession


class BookingItemInline(TabularInline):
    model = BookingItem
    extra = 0


@admin.action(description="Mark selected requests as Contacted")
def mark_contacted(modeladmin, request, queryset):
    from django.utils import timezone

    queryset.filter(first_response_at__isnull=True).update(first_response_at=timezone.now())
    queryset.update(status=BookingRequest.Status.CONTACTED)


@admin.action(description="Mark selected requests as Confirmed")
def mark_confirmed(modeladmin, request, queryset):
    queryset.update(status=BookingRequest.Status.CONFIRMED)


@admin.action(description="Export selected as CSV")
def export_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="booking_requests.csv"'
    writer = csv.writer(response)
    writer.writerow(
        [
            "Ref code",
            "Full name",
            "Email",
            "Phone",
            "WhatsApp",
            "Country",
            "Status",
            "Source",
            "Start date",
            "End date",
            "Adults",
            "Children",
            "Estimated total (USD)",
            "Created at",
        ]
    )
    for booking in queryset:
        writer.writerow(
            [
                booking.ref_code,
                booking.full_name,
                booking.email,
                booking.phone,
                booking.whatsapp,
                booking.country,
                booking.get_status_display(),
                booking.get_source_type_display(),
                booking.start_date,
                booking.end_date,
                booking.adults,
                booking.children,
                booking.estimated_total_usd,
                booking.created_at,
            ]
        )
    return response


# Colour-coded status badges (CLAUDE.md §11) via unfold's @display(label=...)
# — keys must match BookingRequest.get_status_display() exactly, since that's
# the value the decorated method returns.
_STATUS_LABELS = {
    "New": "info",
    "Contacted": "primary",
    "Quoted": "warning",
    "Confirmed": "success",
    "Completed": "success",
    "Cancelled": "danger",
}


@admin.register(BookingRequest)
class BookingRequestAdmin(ModelAdmin):
    list_display = (
        "ref_code",
        "full_name",
        "status_badge",
        "source_type",
        "start_date",
        "adults",
        "children",
        "estimated_total_usd",
        "whatsapp_link",
        "created_at",
    )
    list_filter = ("status", "source_type", "start_date", "created_at")
    search_fields = ("ref_code", "full_name", "email", "phone", "whatsapp")
    date_hierarchy = "created_at"
    inlines = [BookingItemInline]
    actions = [mark_contacted, mark_confirmed, export_csv]
    readonly_fields = ("ref_code", "created_at")

    @display(description="Status", ordering="status", label=_STATUS_LABELS)
    def status_badge(self, obj):
        return obj.get_status_display()

    @admin.display(description="WhatsApp")
    def whatsapp_link(self, obj):
        number = obj.whatsapp or obj.phone
        if not number:
            return "—"
        digits = "".join(ch for ch in number if ch.isdigit())
        return format_html(
            '<a href="https://wa.me/{}" target="_blank" rel="noopener" '
            'class="font-semibold text-green-600 dark:text-green-400">💬 Chat</a>',
            digits,
        )


@admin.register(BookingItem)
class BookingItemAdmin(ModelAdmin):
    list_display = ("request", "item_type", "label", "unit_price_usd", "quantity", "subtotal_usd")
    list_filter = ("item_type",)


@admin.register(BuilderSession)
class BuilderSessionAdmin(ModelAdmin):
    list_display = ("session_key", "last_step", "estimated_total_usd", "is_converted", "created_at")
    list_filter = ("is_converted", "last_step")
