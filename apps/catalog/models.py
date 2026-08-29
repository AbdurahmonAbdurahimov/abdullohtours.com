"""
Catalog models: destinations, attractions, the fleet, and everything that
feeds the pricing engine (apps/catalog/pricing.py) — vehicle classes,
activities, add-ons, packages and seasonal rates.

NOTE on "images"/"gallery" fields: CLAUDE.md §4 lists these as plain fields
without specifying a gallery model. Rather than invent a separate Image model
in this scaffold pass, we use a JSONField storing a list of media paths/URLs
(`images`/`gallery`) alongside a single primary ImageField (`hero_image` /
`cover_image`) for the "hero" shot. The primary ImageField is a
`WebPImageField` (apps/core/fields.py) — §7's WebP conversion/responsive
srcset pipeline runs on it automatically; the JSONField gallery entries are
out of scope for that pipeline since they aren't real ImageFields. Revisit
if a real gallery/ordering UI is needed.
"""

from django.db import models
from django.urls import reverse
from django.utils import translation
from django.utils.translation import gettext

from apps.core.fields import WebPImageField
from apps.core.models import SEOMixin


class Destination(SEOMixin):
    slug = models.SlugField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    region = models.CharField(max_length=255, blank=True)
    hero_image = WebPImageField(
        upload_to="destinations/",
        blank=True,
        null=True,
        width_field="hero_image_width",
        height_field="hero_image_height",
    )
    hero_image_width = models.PositiveIntegerField(null=True, blank=True, editable=False)
    hero_image_height = models.PositiveIntegerField(null=True, blank=True, editable=False)
    intro = models.TextField(blank=True)
    body = models.TextField(blank=True)
    min_recommended_days = models.PositiveSmallIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        # Always the canonical EN URL (drives the admin's "View on site"
        # link) regardless of the current admin user's active locale.
        with translation.override("en"):
            return reverse("catalog:destination_detail", kwargs={"slug": self.slug})


class Attraction(models.Model):
    destination = models.ForeignKey(
        Destination, on_delete=models.CASCADE, related_name="attractions"
    )
    name = models.CharField(max_length=255)
    images = models.JSONField(default=list, blank=True, help_text="List of image paths/URLs.")
    description = models.TextField(blank=True)
    entry_fee_usd = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    typical_duration_min = models.PositiveIntegerField(
        default=60, help_text="Typical visit duration, in minutes."
    )
    # Attractions themselves are not directly bookable line items — they are
    # informational unless/until surfaced as an Activity by the same name.
    is_bookable = models.BooleanField(default=False)

    class Meta:
        ordering = ["destination__order", "name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.destination.name})"


class VehicleClass(models.Model):
    name = models.CharField(max_length=100)
    min_pax = models.PositiveSmallIntegerField()
    max_pax = models.PositiveSmallIntegerField()
    daily_rate_usd = models.DecimalField(max_digits=8, decimal_places=2)
    image = WebPImageField(
        upload_to="vehicle_classes/",
        blank=True,
        null=True,
        width_field="image_width",
        height_field="image_height",
    )
    image_width = models.PositiveIntegerField(null=True, blank=True, editable=False)
    image_height = models.PositiveIntegerField(null=True, blank=True, editable=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "min_pax"]

    def __str__(self) -> str:
        return f"{self.name} ({self.min_pax}-{self.max_pax} pax)"


class Activity(SEOMixin):
    class PriceType(models.TextChoices):
        PER_VEHICLE = "PER_VEHICLE", "Per vehicle (flat, per group)"
        PER_PERSON = "PER_PERSON", "Per person"
        PER_DAY = "PER_DAY", "Per day"

    destination = models.ForeignKey(
        Destination, on_delete=models.CASCADE, related_name="activities"
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    price_type = models.CharField(max_length=20, choices=PriceType.choices)
    base_price_usd = models.DecimalField(max_digits=8, decimal_places=2)
    duration_hours = models.DecimalField(max_digits=4, decimal_places=1, default=1)
    images = models.JSONField(default=list, blank=True)
    short_desc = models.CharField(max_length=320, blank=True)
    full_desc = models.TextField(blank=True)
    included = models.TextField(blank=True, help_text="One item per line.")
    not_included = models.TextField(blank=True, help_text="One item per line.")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["destination__order", "title"]
        verbose_name_plural = "Activities"

    def __str__(self) -> str:
        return self.title


class AddOn(models.Model):
    class Unit(models.TextChoices):
        PER_PERSON = "PER_PERSON", "Per person"
        PER_DAY = "PER_DAY", "Per day"
        PER_GROUP = "PER_GROUP", "Per group"
        PER_NIGHT = "PER_NIGHT", "Per night"

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price_usd = models.DecimalField(max_digits=8, decimal_places=2)
    unit = models.CharField(max_length=20, choices=Unit.choices)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.get_unit_display()})"


class Package(SEOMixin):
    class Tier(models.TextChoices):
        ECONOMY = "ECONOMY", "Economy"
        STANDARD = "STANDARD", "Standard"
        PREMIUM = "PREMIUM", "Premium"

    slug = models.SlugField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    tier = models.CharField(max_length=20, choices=Tier.choices, default=Tier.STANDARD)
    total_days = models.PositiveSmallIntegerField()
    summary = models.CharField(max_length=320, blank=True)
    body = models.TextField(blank=True)
    hero_image = WebPImageField(
        upload_to="packages/",
        blank=True,
        null=True,
        width_field="hero_image_width",
        height_field="hero_image_height",
    )
    hero_image_width = models.PositiveIntegerField(null=True, blank=True, editable=False)
    hero_image_height = models.PositiveIntegerField(null=True, blank=True, editable=False)
    gallery = models.JSONField(default=list, blank=True)
    base_vehicle_class = models.ForeignKey(
        VehicleClass, on_delete=models.PROTECT, related_name="packages"
    )
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["title"]

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        with translation.override("en"):
            return reverse("catalog:package_detail", kwargs={"slug": self.slug})


class PackageDay(models.Model):
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name="days")
    day_number = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["package", "day_number"]
        unique_together = ("package", "day_number")

    def __str__(self) -> str:
        return f"{self.package.title} — Day {self.day_number}"


class PackageItem(models.Model):
    package_day = models.ForeignKey(PackageDay, on_delete=models.CASCADE, related_name="items")
    activity = models.ForeignKey(
        Activity, on_delete=models.PROTECT, null=True, blank=True, related_name="package_items"
    )
    addon = models.ForeignKey(
        AddOn, on_delete=models.PROTECT, null=True, blank=True, related_name="package_items"
    )
    is_optional = models.BooleanField(default=False)
    custom_label = models.CharField(
        max_length=255, blank=True, help_text="Used when neither activity nor addon applies."
    )

    class Meta:
        ordering = ["package_day", "id"]

    def __str__(self) -> str:
        label = (
            self.custom_label
            or (self.activity and self.activity.title)
            or (self.addon and self.addon.name)
        )
        return f"{self.package_day} — {label}"


class SeasonalRate(models.Model):
    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="seasonal_rates",
        help_text="Leave blank to apply this rate globally to all activities.",
    )
    date_from = models.DateField()
    date_to = models.DateField()
    multiplier = models.DecimalField(
        max_digits=4, decimal_places=2, default=1, help_text="e.g. 1.20 for +20% peak season."
    )
    label = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["date_from"]

    def __str__(self) -> str:
        scope = self.activity.title if self.activity else "Global"
        return f"{scope}: {self.date_from} – {self.date_to} (x{self.multiplier})"


class Vehicle(models.Model):
    name = models.CharField(max_length=255)
    vehicle_class = models.ForeignKey(
        VehicleClass, on_delete=models.PROTECT, related_name="vehicles"
    )
    plate = models.CharField(max_length=32, blank=True)
    is_partner = models.BooleanField(
        default=False, help_text="Third-party partner vehicle rather than company-owned."
    )
    is_active = models.BooleanField(default=True)
    daily_cost_usd = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    class Meta:
        ordering = ["vehicle_class", "name"]

    def __str__(self) -> str:
        return self.name


class Driver(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=32, blank=True)
    languages = models.CharField(max_length=255, blank=True, help_text="Comma-separated.")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class RoutePage(SEOMixin):
    """Programmatic SEO landing page (CLAUDE.md §13 Phase 3) for a pair of
    destinations, e.g. "Samarkand & Bukhara Tour" — targets long-tail
    searches that a single-destination page doesn't rank for.

    Deliberately has no free-text body field: the page is composed at render
    time from destination_a/destination_b's own (already-translated) intro
    copy and attractions, so it scales by adding Destination rows rather than
    needing hand-written content per pair. `title`/`meta_title` are likewise
    derived properties, not stored fields — this keeps the model "spec-free"
    (CLAUDE.md §4 doesn't define this model) but still fully translated,
    since `destination.name` already resolves per-language via
    modeltranslation.
    """

    slug = models.SlugField(max_length=255, unique=True)
    destination_a = models.ForeignKey(
        Destination, on_delete=models.CASCADE, related_name="route_pages_as_a"
    )
    destination_b = models.ForeignKey(
        Destination, on_delete=models.CASCADE, related_name="route_pages_as_b"
    )
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "slug"]
        unique_together = ("destination_a", "destination_b")

    def __str__(self) -> str:
        return f"{self.destination_a.name} & {self.destination_b.name}"

    def get_absolute_url(self) -> str:
        with translation.override("en"):
            return reverse("catalog:route_detail", kwargs={"slug": self.slug})

    @property
    def title(self) -> str:
        # Translators: %(a)s and %(b)s are destination names, e.g. "Samarkand"
        # and "Bukhara" — resolved per-language via modeltranslation already,
        # so only the surrounding phrase needs translating here.
        return gettext("%(a)s & %(b)s Tour") % {
            "a": self.destination_a.name,
            "b": self.destination_b.name,
        }

    @property
    def combined_min_days(self) -> int:
        return self.destination_a.min_recommended_days + self.destination_b.min_recommended_days


class BlackoutDate(models.Model):
    date = models.DateField()
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="blackout_dates",
        help_text="Leave blank to block this date for the entire fleet.",
    )
    reason = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["date"]

    def __str__(self) -> str:
        scope = self.vehicle.name if self.vehicle else "All vehicles"
        return f"{self.date} — {scope}"
