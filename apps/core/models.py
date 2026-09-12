from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
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
    translation_complete_ar = models.BooleanField(default=False)

    class Meta:
        abstract = True


class GalleryImage(models.Model):
    """One uploaded photo in a model's gallery, attached generically via
    `content_type`/`object_id` so every gallery on the site (Attraction,
    Activity, Package, Hotel, Car, ...) shares one uploadable, orderable
    admin inline instead of a hand-typed JSONField of URLs.

    Add a `GenericRelation(GalleryImage)` on any parent model that needs a
    gallery, then attach `apps.core.admin_mixins.GalleryImageInline` to its
    ModelAdmin.
    """

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    image = WebPImageField(
        upload_to="gallery/",
        width_field="image_width",
        height_field="image_height",
    )
    image_width = models.PositiveIntegerField(null=True, blank=True, editable=False)
    image_height = models.PositiveIntegerField(null=True, blank=True, editable=False)
    caption = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        indexes = [models.Index(fields=["content_type", "object_id"])]

    def __str__(self) -> str:
        return self.caption or f"Gallery image #{self.pk}"


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


class LoginEvent(models.Model):
    """Audit trail of admin/staff sign-in activity.

    Recorded from `django.contrib.auth.signals` (see `apps.core.signals`) so
    every login, logout and failed attempt against `/admin/` is captured
    regardless of which view handled auth — no dependence on middleware
    running first. `user` is nullable because a failed attempt against a
    username that doesn't exist has no user to point at; `username_attempted`
    keeps that case auditable anyway.
    """

    class EventType(models.TextChoices):
        LOGIN = "LOGIN", "Login"
        LOGOUT = "LOGOUT", "Logout"
        FAILED = "FAILED", "Failed attempt"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="login_events",
    )
    username_attempted = models.CharField(
        max_length=150,
        blank=True,
        help_text="Set for FAILED events where the username didn't match a user.",
    )
    event_type = models.CharField(max_length=10, choices=EventType.choices)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    session_key = models.CharField(max_length=40, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["event_type", "-created_at"]),
        ]

    def __str__(self) -> str:
        who = self.user.get_username() if self.user_id else self.username_attempted or "unknown"
        return f"{self.get_event_type_display()} · {who} · {self.created_at:%d %b %Y %H:%M}"


class ActiveSession(models.Model):
    """One currently-live browser session for a staff/admin user.

    Created on login and refreshed on every request by
    `apps.core.middleware.TrackActiveSessionMiddleware` (throttled — see
    that module) so "who's online right now" and "last seen" are both
    answerable without polling the session store directly. Deleted on
    logout; stale rows (browser closed without logging out) are pruned by
    the `prune_stale_sessions` cron command using Django's own session
    expiry as the cutoff, mirroring how `django_session` itself expires.

    Only staff users are tracked — this is an internal ops tool, not
    analytics on tourist site visitors.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="active_sessions",
    )
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_seen_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-last_seen_at"]
        indexes = [models.Index(fields=["user", "-last_seen_at"])]

    def __str__(self) -> str:
        return f"{self.user.get_username()} · {self.ip_address or 'unknown IP'}"
