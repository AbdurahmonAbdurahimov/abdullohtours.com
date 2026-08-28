import random
import string

from django.db import models

from apps.catalog.models import Package, VehicleClass


def _generate_ref_code() -> str:
    """e.g. 'AB-8291' — short, speakable over WhatsApp/phone."""
    digits = "".join(random.choices(string.digits, k=4))
    return f"AB-{digits}"


class BookingRequest(models.Model):
    """A booking *request*, not a sale — there is no online payment (CLAUDE.md §1).

    The tourist submits this, we get a Telegram notification, and an admin
    follows up on WhatsApp to agree the final price. `status` tracks that
    human conversation through to a confirmed/completed trip.
    """

    class Status(models.TextChoices):
        NEW = "NEW", "New"
        CONTACTED = "CONTACTED", "Contacted"
        QUOTED = "QUOTED", "Quoted"
        CONFIRMED = "CONFIRMED", "Confirmed"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    class SourceType(models.TextChoices):
        # DIRECT: the short-form booking request form (CLAUDE.md §6) with no
        # builder/package context. BUILDER: submitted at the end of the Tour
        # Builder flow (Phase 2) via a BuilderSession. PACKAGE: "book this
        # package" from a Package detail page (a package with no builder
        # customisation). Kept as an explicit enum rather than inferring
        # source from `package`/`custom_payload` being set, so it's directly
        # filterable in the admin (CLAUDE.md §11: filter by status/date/source).
        DIRECT = "DIRECT", "Direct request"
        BUILDER = "BUILDER", "Tour builder"
        PACKAGE = "PACKAGE", "Package page"

    ref_code = models.CharField(max_length=16, unique=True, editable=False)
    source_type = models.CharField(max_length=20, choices=SourceType.choices)
    package = models.ForeignKey(
        Package, on_delete=models.SET_NULL, null=True, blank=True, related_name="booking_requests"
    )
    custom_payload = models.JSONField(
        default=dict, blank=True, help_text="Raw builder selection, if source_type=BUILDER."
    )

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    adults = models.PositiveSmallIntegerField(default=1)
    children = models.PositiveSmallIntegerField(default=0)
    vehicle_class = models.ForeignKey(
        VehicleClass,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="booking_requests",
    )

    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=32, blank=True)
    whatsapp = models.CharField(max_length=32, blank=True)
    country = models.CharField(max_length=100, blank=True)
    message = models.TextField(blank=True)
    preferred_language = models.CharField(max_length=8, default="en")

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    estimated_total_usd = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    quoted_total_usd = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    admin_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    # Response-time is THE key business metric (CLAUDE.md §1) — this is what
    # check_unanswered_requests.py watches to trigger a reminder ping.
    first_response_at = models.DateTimeField(null=True, blank=True)

    utm_source = models.CharField(max_length=100, blank=True)
    utm_medium = models.CharField(max_length=100, blank=True)
    utm_campaign = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.ref_code} — {self.full_name}"

    def save(self, *args, **kwargs):
        if not self.ref_code:
            code = _generate_ref_code()
            while BookingRequest.objects.filter(ref_code=code).exists():
                code = _generate_ref_code()
            self.ref_code = code
        super().save(*args, **kwargs)


class BookingItem(models.Model):
    """A frozen line item on a BookingRequest.

    Deliberately plain fields (label/unit_price_usd/quantity/subtotal_usd)
    rather than a live FK to Activity/AddOn with a computed price: CLAUDE.md
    §4 is explicit that if an admin changes an Activity's price tomorrow,
    existing requests must not change. We snapshot the price + label at
    request time, the same way an invoice line item works.
    """

    class ItemType(models.TextChoices):
        TRANSPORT = "TRANSPORT", "Transport"
        ACTIVITY = "ACTIVITY", "Activity"
        ADDON = "ADDON", "Add-on"

    request = models.ForeignKey(BookingRequest, on_delete=models.CASCADE, related_name="items")
    item_type = models.CharField(max_length=20, choices=ItemType.choices)
    label = models.CharField(max_length=255)
    unit_price_usd = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.DecimalField(max_digits=8, decimal_places=2, default=1)
    subtotal_usd = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ["id"]

    def __str__(self) -> str:
        return f"{self.request.ref_code}: {self.label}"


class BuilderSession(models.Model):
    """Tracks an in-progress (possibly abandoned) Tour Builder session.

    Persisted on every step change so abandoned builders are visible in the
    admin dashboard (CLAUDE.md §6/§11) — Phase 2 work, modelled now.
    """

    session_key = models.CharField(max_length=64, db_index=True)
    payload = models.JSONField(default=dict, blank=True)
    last_step = models.PositiveSmallIntegerField(default=1)
    estimated_total_usd = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    is_converted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"BuilderSession({self.session_key}) step {self.last_step}"
