from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from .models import BookingItem, BookingRequest, BuilderSession

# NOTE: colour-coded status badges, one-click WhatsApp links, the custom
# dashboard (today's requests / pending count / confirmed this month /
# estimated revenue / abandoned builders) and CSV export bulk action
# (CLAUDE.md §11) are follow-up work on top of this scaffold pass. Bulk
# "mark contacted" / "mark confirmed" actions are stubbed below since
# they're cheap to add now and directly useful.


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


@admin.register(BookingRequest)
class BookingRequestAdmin(ModelAdmin):
    list_display = (
        "ref_code",
        "full_name",
        "status",
        "source_type",
        "start_date",
        "adults",
        "children",
        "estimated_total_usd",
        "created_at",
    )
    list_filter = ("status", "source_type", "start_date", "created_at")
    search_fields = ("ref_code", "full_name", "email", "phone", "whatsapp")
    date_hierarchy = "created_at"
    inlines = [BookingItemInline]
    actions = [mark_contacted, mark_confirmed]
    readonly_fields = ("ref_code", "created_at")


@admin.register(BookingItem)
class BookingItemAdmin(ModelAdmin):
    list_display = ("request", "item_type", "label", "unit_price_usd", "quantity", "subtotal_usd")
    list_filter = ("item_type",)


@admin.register(BuilderSession)
class BuilderSessionAdmin(ModelAdmin):
    list_display = ("session_key", "last_step", "estimated_total_usd", "is_converted", "created_at")
    list_filter = ("is_converted", "last_step")
