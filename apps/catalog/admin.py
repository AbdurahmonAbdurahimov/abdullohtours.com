from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from unfold.admin import ModelAdmin, TabularInline

from .models import (
    Activity,
    AddOn,
    Attraction,
    BlackoutDate,
    Destination,
    Driver,
    Package,
    PackageDay,
    PackageItem,
    RoutePage,
    SeasonalRate,
    Vehicle,
    VehicleClass,
)

# NOTE: colour-coded status badges, one-click WhatsApp links and CSV export
# (CLAUDE.md §11) apply to BookingRequest (see apps/bookings/admin.py), not
# here. This pass focuses on getting every catalog model registered and
# usable in django-unfold with sensible list/filter/search config.


class AttractionInline(TabularInline):
    model = Attraction
    extra = 0


@admin.register(Destination)
class DestinationAdmin(TranslationAdmin, ModelAdmin):
    list_display = ("name", "region", "min_recommended_days", "is_active", "order")
    list_filter = ("is_active", "region")
    search_fields = ("name", "region")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [AttractionInline]
    # Per-language translation status column (CLAUDE.md §11: "content models
    # show a per-language translation status column so gaps are visible").
    readonly_fields = ()

    def get_list_display(self, request):
        return (*super().get_list_display(request), "translation_status")

    @admin.display(description="Translations")
    def translation_status(self, obj):
        flags = {
            "RU": obj.translation_complete_ru,
            "DE": obj.translation_complete_de,
            "FR": obj.translation_complete_fr,
            "ES": obj.translation_complete_es,
        }
        return ", ".join(f"{code}✓" if done else f"{code}✗" for code, done in flags.items())


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
class ActivityAdmin(TranslationAdmin, ModelAdmin):
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
class PackageAdmin(TranslationAdmin, ModelAdmin):
    list_display = ("title", "tier", "total_days", "base_vehicle_class", "is_featured", "is_active")
    list_filter = ("tier", "is_active", "is_featured")
    search_fields = ("title",)
    prepopulated_fields = {"slug": ("title",)}
    inlines = [PackageDayInline]


@admin.register(PackageDay)
class PackageDayAdmin(ModelAdmin):
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
class RoutePageAdmin(TranslationAdmin, ModelAdmin):
    list_display = ("__str__", "slug", "is_active", "order")
    list_filter = ("is_active",)
    autocomplete_fields = ("destination_a", "destination_b")


@admin.register(BlackoutDate)
class BlackoutDateAdmin(ModelAdmin):
    list_display = ("date", "vehicle", "reason")
    list_filter = ("vehicle",)
    date_hierarchy = "date"
