from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from unfold.admin import ModelAdmin, TabularInline

from apps.core.admin_mixins import TranslationStatusMixin

from .models import (
    Activity,
    AddOn,
    Attraction,
    BlackoutDate,
    Car,
    Destination,
    Driver,
    Hotel,
    Package,
    PackageDay,
    PackageItem,
    RoutePage,
    SeasonalRate,
    Vehicle,
    VehicleClass,
)

# Colour-coded status badges, one-click WhatsApp links and CSV export
# (CLAUDE.md §11) apply to BookingRequest — see apps/bookings/admin.py.
# Every content model with SEOMixin gets a translation-status column via
# TranslationStatusMixin (apps/core/admin_mixins.py).


class AttractionInline(TabularInline):
    model = Attraction
    extra = 0


@admin.register(Destination)
class DestinationAdmin(TranslationStatusMixin, TranslationAdmin, ModelAdmin):
    list_display = ("name", "region", "min_recommended_days", "is_active", "order")
    list_filter = ("is_active", "region")
    search_fields = ("name", "region")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [AttractionInline]


@admin.register(Attraction)
class AttractionAdmin(ModelAdmin):
    list_display = ("name", "destination", "entry_fee_usd", "typical_duration_min", "is_bookable")
    list_filter = ("destination", "is_bookable")
    search_fields = ("name",)


@admin.register(VehicleClass)
class VehicleClassAdmin(ModelAdmin):
    list_display = ("name", "min_pax", "max_pax", "daily_rate_usd", "order")
    ordering = ("order",)


@admin.register(Activity)
class ActivityAdmin(TranslationStatusMixin, TranslationAdmin, ModelAdmin):
    list_display = ("title", "destination", "price_type", "base_price_usd", "is_active")
    list_filter = ("destination", "price_type", "is_active")
    search_fields = ("title",)
    prepopulated_fields = {"slug": ("title",)}


@admin.register(AddOn)
class AddOnAdmin(ModelAdmin):
    list_display = ("name", "unit", "price_usd", "is_active")
    list_filter = ("unit", "is_active")
    search_fields = ("name",)


class PackageItemInline(TabularInline):
    model = PackageItem
    extra = 0


class PackageDayInline(TabularInline):
    model = PackageDay
    extra = 0


@admin.register(Package)
class PackageAdmin(TranslationStatusMixin, TranslationAdmin, ModelAdmin):
    list_display = ("title", "tier", "total_days", "base_vehicle_class", "is_featured", "is_active")
    list_filter = ("tier", "is_active", "is_featured")
    search_fields = ("title",)
    prepopulated_fields = {"slug": ("title",)}
    inlines = [PackageDayInline]


@admin.register(PackageDay)
class PackageDayAdmin(TranslationAdmin, ModelAdmin):
    list_display = ("package", "day_number", "title")
    list_filter = ("package",)
    inlines = [PackageItemInline]


@admin.register(PackageItem)
class PackageItemAdmin(ModelAdmin):
    list_display = ("package_day", "activity", "addon", "is_optional")
    list_filter = ("is_optional",)


@admin.register(SeasonalRate)
class SeasonalRateAdmin(ModelAdmin):
    list_display = ("label", "activity", "date_from", "date_to", "multiplier")
    list_filter = ("activity",)


@admin.register(Vehicle)
class VehicleAdmin(ModelAdmin):
    list_display = ("name", "vehicle_class", "plate", "is_partner", "is_active", "daily_cost_usd")
    list_filter = ("vehicle_class", "is_partner", "is_active")
    search_fields = ("name", "plate")


@admin.register(Driver)
class DriverAdmin(ModelAdmin):
    list_display = ("name", "phone", "languages", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)


@admin.register(RoutePage)
class RoutePageAdmin(TranslationStatusMixin, TranslationAdmin, ModelAdmin):
    list_display = ("__str__", "slug", "is_active", "order")
    list_filter = ("is_active",)
    autocomplete_fields = ("destination_a", "destination_b")


@admin.register(Hotel)
class HotelAdmin(TranslationStatusMixin, TranslationAdmin, ModelAdmin):
    list_display = ("name", "category", "destination", "price_per_night_usd", "is_active", "order")
    list_filter = ("category", "destination", "is_active")
    search_fields = ("name", "address")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Car)
class CarAdmin(TranslationStatusMixin, TranslationAdmin, ModelAdmin):
    list_display = ("name", "category", "capacity_pax", "daily_rate_usd", "is_active", "order")
    list_filter = ("category", "is_active")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(BlackoutDate)
class BlackoutDateAdmin(ModelAdmin):
    list_display = ("date", "vehicle", "reason")
    list_filter = ("vehicle",)
    date_hierarchy = "date"
