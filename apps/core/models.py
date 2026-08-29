from django.db import models

from .fields import WebPImageField


class SiteSettings(models.Model):
    """Singleton row holding site-wide contact details and defaults.

    Templates must always read contact details from this model via the
    `apps.core.context_processors.site_settings` context processor —
    never hardcode a phone number / WhatsApp link / social handle.
    """

    phone = models.CharField(max_length=32)
    whatsapp_number = models.CharField(
        max_length=32, help_text="Digits only, no '+', e.g. 998953336000"
    )
    telegram_username = models.CharField(max_length=64)
    instagram_username = models.CharField(max_length=64)
    email = models.EmailField(blank=True)
    office_address = models.CharField(max_length=255, blank=True)
    working_hours = models.CharField(max_length=255, blank=True)
    response_time_promise = models.CharField(
        max_length=255,
        blank=True,
        help_text="e.g. 'We reply within 1 hour' — shown near booking CTAs.",
    )
    default_og_image = WebPImageField(
        upload_to="site/",
        blank=True,
        null=True,
        width_field="default_og_image_width",
        height_field="default_og_image_height",
    )
    default_og_image_width = models.PositiveIntegerField(null=True, blank=True, editable=False)
    default_og_image_height = models.PositiveIntegerField(null=True, blank=True, editable=False)

    class Meta:
        verbose_name = "Site settings"
        verbose_name_plural = "Site settings"

    def __str__(self) -> str:
        return "Site settings"

    def save(self, *args, **kwargs):
        # Enforce singleton: always the same row.
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Singleton row must not be deleted from the admin.
        pass

    @classmethod
    def load(cls) -> "SiteSettings":
        obj, _created = cls.objects.get_or_create(
            pk=1,
            defaults={
                "phone": "+998953336000",
                "whatsapp_number": "998953336000",
                "telegram_username": "abdulloh_talibdjanov",
                "instagram_username": "abdulloh_tours",
                # Left blank rather than a fake placeholder string: these are
                # typed/validated fields (EmailField) and get rendered raw in
                # public templates (footer, contact page) — an invalid or
                # junk value would either break admin saves or leak onto the
                # live site. Templates hide each field's UI when it's empty;
                # fill in the real values in the admin once known.
                "email": "",
                "office_address": "",
                "working_hours": "",
                "response_time_promise": "",
            },
        )
        return obj


class ExchangeRate(models.Model):
    """Daily-cached USD -> currency conversion rate, refreshed by
    `update_exchange_rates` (cron, CLAUDE.md §9). Prices are always stored
    and quoted in USD (CLAUDE.md §12); EUR/GBP/UZS are an informational
    display-only conversion computed from these cached rows — never the
    source of truth for a price.

    Lives on `apps.core` (rather than a new app) since it's a small,
    site-wide utility table with no natural home in catalog/bookings/blog/
    notifications.
    """

    currency = models.CharField(
        max_length=3, unique=True, help_text="ISO 4217, e.g. EUR, GBP, UZS."
    )
    rate_from_usd = models.DecimalField(
        max_digits=14, decimal_places=6, help_text="1 USD = this many units of `currency`."
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["currency"]

    def __str__(self) -> str:
        return f"1 USD = {self.rate_from_usd} {self.currency}"


class SEOMixin(models.Model):
    """Abstract mixin adding standard SEO fields to translatable content models.

    `translation_complete_ru/de/fr/es` gate hreflang emission per CLAUDE.md §7
    ("a language variant must only emit hreflang when its translation is
    actually complete"). We use one boolean flag per language on this mixin
    rather than inspecting individual modeltranslation fields for blankness —
    it's simpler to reason about and consistent across every translatable
    content type (Destination, Activity, Package, BlogPost), instead of each
    model needing its own bespoke "is this fully translated" check.
    """

    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.CharField(max_length=320, blank=True)
    focus_keyword = models.CharField(max_length=255, blank=True)
    og_image = WebPImageField(
        upload_to="seo/",
        blank=True,
        null=True,
        width_field="og_image_width",
        height_field="og_image_height",
    )
    og_image_width = models.PositiveIntegerField(null=True, blank=True, editable=False)
    og_image_height = models.PositiveIntegerField(null=True, blank=True, editable=False)
    noindex = models.BooleanField(default=False)

    translation_complete_ru = models.BooleanField(default=False)
    translation_complete_de = models.BooleanField(default=False)
    translation_complete_fr = models.BooleanField(default=False)
    translation_complete_es = models.BooleanField(default=False)

    class Meta:
        abstract = True


class Review(models.Model):
    """A traveller review (Phase 2, CLAUDE.md §13).

    Not a SEOMixin/translatable content model — this is quoted third-party
    testimony, not editorial copy we author, so it's displayed as submitted
    rather than translated. `is_published` defaults to False as a safety
    rail: nothing appears on /reviews/ until an admin has verified it's a
    real review, not a placeholder. This app deliberately ships with zero
    seeded rows — fabricating "sample" reviews would be fake testimonials,
    which is a different and worse problem than an empty page with a
    TODO notice.
    """

    class Source(models.TextChoices):
        GOOGLE = "GOOGLE", "Google"
        TRIPADVISOR = "TRIPADVISOR", "TripAdvisor"
        DIRECT = "DIRECT", "Direct / WhatsApp"
        OTHER = "OTHER", "Other"

    author_name = models.CharField(max_length=255)
    country = models.CharField(max_length=100, blank=True)
    rating = models.PositiveSmallIntegerField(help_text="1–5")
    body = models.TextField()
    source = models.CharField(max_length=20, choices=Source.choices, default=Source.DIRECT)
    source_url = models.URLField(blank=True, help_text="Link to the original review, if public.")
    package = models.ForeignKey(
        "catalog.Package", on_delete=models.SET_NULL, null=True, blank=True, related_name="reviews"
    )
    destination = models.ForeignKey(
        "catalog.Destination",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviews",
    )
    is_published = models.BooleanField(
        default=False, help_text="Only verified, real reviews should be published."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.author_name} ({self.rating}★)"
