"""
Catalog models: destinations, attractions, the fleet, and everything that
feeds the pricing engine (apps/catalog/pricing.py) — vehicle classes,
activities, add-ons, packages and seasonal rates.

NOTE on "images"/"gallery" fields: CLAUDE.md §4 lists these as plain fields
without specifying a gallery model. Rather than invent a separate Image model
in this scaffold pass, we use a JSONField storing a list of media paths/URLs
(`images`/`gallery`) alongside a single primary ImageField (`hero_image` /
`cover_image`) for the "hero" shot. This keeps §7's WebP/srcset/lazy-load
pipeline free to operate on the primary image without over-building a media
model that isn't specified. Revisit if a real gallery/ordering UI is needed.
"""

from django.db import models

from apps.core.models import SEOMixin


class Destination(SEOMixin):
    slug = models.SlugField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    region = models.CharField(max_length=255, blank=True)
    hero_image = models.ImageField(upload_to="destinations/", blank=True, null=True)
    intro = models.TextField(blank=True)
    body = models.TextField(blank=True)
    min_recommended_days = models.PositiveSmallIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self) -> str:
        return self.name


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
    image = models.ImageField(upload_to="vehicle_classes/", blank=True, null=True)
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
    hero_image = models.ImageField(upload_to="packages/", blank=True, null=True)
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
