"""
Base settings shared by all environments.

Environment variables are read via django-environ from a `.env` file at the
project root (see `.env.example` for the full list of variables this project
uses). Individual environments (dev.py / prod.py) import * from this module
and override what they need.
"""

from pathlib import Path

import environ
from django.templatetags.static import static
from django.urls import reverse_lazy

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(
    DEBUG=(bool, False),
)
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY", default="django-insecure-dev-only-change-me")

DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

# Canonical production host, used for building absolute URLs in sitemaps,
# canonical <link> tags and JSON-LD (no online payment / no www — see CLAUDE.md).
CANONICAL_HOST = env("CANONICAL_HOST", default="https://abdullohtours.com")

# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------
# django-unfold and django-modeltranslation must both be listed BEFORE
# django.contrib.admin: unfold replaces the default admin site/templates,
# and modeltranslation patches the admin machinery at import time.
INSTALLED_APPS = [
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "unfold.contrib.inlines",
    "modeltranslation",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "django.contrib.humanize",
    "django_ratelimit",
    # Local apps
    "apps.core",
    "apps.catalog",
    "apps.bookings",
    "apps.blog",
    "apps.notifications",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
                # Exposes the singleton SiteSettings + CANONICAL_HOST to every
                # template so contact details are never hardcoded (CLAUDE.md).
                "apps.core.context_processors.site_settings",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# ---------------------------------------------------------------------------
# Database — PostgreSQL is fixed by spec, no sqlite fallback.
# ---------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB", default="abdullohtours"),
        "USER": env("POSTGRES_USER", default="abdullohtours"),
        "PASSWORD": env("POSTGRES_PASSWORD", default="abdullohtours"),
        "HOST": env("POSTGRES_HOST", default="localhost"),
        "PORT": env("POSTGRES_PORT", default="5432"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------------------------
# Internationalisation
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "en"

LANGUAGES = [
    ("en", "English"),
    ("ru", "Русский"),
    ("de", "Deutsch"),
    ("fr", "Français"),
    ("es", "Español"),
]

# modeltranslation needs to know every language it should generate
# translated fields for; keep in sync with LANGUAGES above.
MODELTRANSLATION_DEFAULT_LANGUAGE = "en"
MODELTRANSLATION_LANGUAGES = [code for code, _ in LANGUAGES]

TIME_ZONE = "Asia/Tashkent"
USE_I18N = True
USE_TZ = True

LOCALE_PATHS = [BASE_DIR / "locale"]

# ---------------------------------------------------------------------------
# Static & media files
# ---------------------------------------------------------------------------
STATIC_URL = "static/"
# NOTE: this deliberately does NOT include design/. The design/ folder holds
# throwaway HTML mockups from the design phase (with known defects called
# out in CLAUDE.md — cdn.tailwindcss.com, fake Material colours, googleusercontent
# image URLs, etc). It must never be picked up by collectstatic or shipped to
# production; only static_src/ (the real Tailwind CLI source) is a static dir.
STATICFILES_DIRS = [BASE_DIR / "static_src"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# django-unfold admin theme
# ---------------------------------------------------------------------------
# Gold & Navy (CLAUDE.md §3), per the design/*_gold_navy admin mockups.
# Unfold themes itself entirely off two 11-step colour scales exposed as
# CSS custom properties (--color-primary-*, --color-base-*) — every stop
# below is derived only from CLAUDE.md's own named tokens (gold/gold-bright/
# navy/navy-soft/cream/cream-soft/muted/line), never from the mockups' own
# colours, which are auto-generated Material Design noise CLAUDE.md §3
# explicitly calls out as a defect to ignore. "base" doubles as the
# app-wide neutral scale (backgrounds, borders, body text in both light and
# dark mode) and "primary" as the accent (links, buttons, active nav item,
# focus rings) — deep-merged with unfold's own defaults (e.g. the "font"
# sub-map, which just references these scales by name), so only these two
# need overriding.
UNFOLD = {
    "SITE_TITLE": "Abdulloh Tours Admin",
    "SITE_HEADER": "Abdulloh Tours",
    "SITE_SYMBOL": "map",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "BORDER_RADIUS": "4px",
    "COLORS": {
        "primary": {
            "50": "#FCF2E4",
            "100": "#F5E6CC",
            "200": "#EBD3A3",
            "300": "#DFBD78",
            "400": "#D2AD58",
            "500": "#C9A66B",  # gold
            "600": "#D9A02E",  # gold-bright — CTAs, hover, active nav item
            "700": "#A97F1E",
            "800": "#7D5E16",
            "900": "#52400F",
            "950": "#2E2308",
        },
        "base": {
            "50": "#FFF8F1",  # cream
            "100": "#FCF2E4",  # cream-soft
            "200": "#EDE1D0",
            "300": "#C4C6CC",  # line
            "400": "#9A9CA3",
            "500": "#6E7178",
            "600": "#43474C",  # muted
            "700": "#2E3138",
            "800": "#1B2430",
            "900": "#0A1D2D",  # navy-soft
            "950": "#071A2A",  # navy
        },
    },
    # Forces the sidebar to stay navy chrome regardless of the light/dark
    # toggle (the brand's fixed frame around a theme-able content area,
    # matching the header/footer treatment on the public site) — see
    # static_src/css/admin-theme.css.
    "STYLES": [
        lambda request: static("admin-theme.css"),
    ],
    # Custom dashboard (CLAUDE.md §11) — see apps/core/admin_dashboard.py +
    # templates/admin/index.html.
    "DASHBOARD_CALLBACK": "apps.core.admin_dashboard.dashboard_callback",
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": "Bookings",
                "separator": True,
                "items": [
                    {
                        "title": "Booking requests",
                        "icon": "receipt_long",
                        "link": reverse_lazy("admin:bookings_bookingrequest_changelist"),
                    },
                    {
                        "title": "Booking items",
                        "icon": "list_alt",
                        "link": reverse_lazy("admin:bookings_bookingitem_changelist"),
                    },
                    {
                        "title": "Builder sessions",
                        "icon": "construction",
                        "link": reverse_lazy("admin:bookings_buildersession_changelist"),
                    },
                ],
            },
            {
                "title": "Catalog",
                "separator": True,
                "items": [
                    {
                        "title": "Destinations",
                        "icon": "place",
                        "link": reverse_lazy("admin:catalog_destination_changelist"),
                    },
                    {
                        "title": "Attractions",
                        "icon": "photo_camera",
                        "link": reverse_lazy("admin:catalog_attraction_changelist"),
                    },
                    {
                        "title": "Packages",
                        "icon": "card_travel",
                        "link": reverse_lazy("admin:catalog_package_changelist"),
                    },
                    {
                        "title": "Package days",
                        "icon": "event_note",
                        "link": reverse_lazy("admin:catalog_packageday_changelist"),
                    },
                    {
                        "title": "Package items",
                        "icon": "checklist",
                        "link": reverse_lazy("admin:catalog_packageitem_changelist"),
                    },
                    {
                        "title": "Activities",
                        "icon": "hiking",
                        "link": reverse_lazy("admin:catalog_activity_changelist"),
                    },
                    {
                        "title": "Add-ons",
                        "icon": "add_circle",
                        "link": reverse_lazy("admin:catalog_addon_changelist"),
                    },
                    {
                        "title": "Seasonal rates",
                        "icon": "calendar_month",
                        "link": reverse_lazy("admin:catalog_seasonalrate_changelist"),
                    },
                    {
                        "title": "Vehicle classes",
                        "icon": "directions_car",
                        "link": reverse_lazy("admin:catalog_vehicleclass_changelist"),
                    },
                    {
                        "title": "Route pages (SEO)",
                        "icon": "alt_route",
                        "link": reverse_lazy("admin:catalog_routepage_changelist"),
                    },
                ],
            },
            {
                "title": "Content",
                "separator": True,
                "items": [
                    {
                        "title": "Blog posts",
                        "icon": "article",
                        "link": reverse_lazy("admin:blog_blogpost_changelist"),
                    },
                    {
                        "title": "Reviews",
                        "icon": "reviews",
                        "link": reverse_lazy("admin:core_review_changelist"),
                    },
                ],
            },
            {
                "title": "Fleet",
                "separator": True,
                "items": [
                    {
                        "title": "Vehicles",
                        "icon": "airport_shuttle",
                        "link": reverse_lazy("admin:catalog_vehicle_changelist"),
                    },
                    {
                        "title": "Drivers",
                        "icon": "badge",
                        "link": reverse_lazy("admin:catalog_driver_changelist"),
                    },
                    {
                        "title": "Blackout dates",
                        "icon": "event_busy",
                        "link": reverse_lazy("admin:catalog_blackoutdate_changelist"),
                    },
                ],
            },
            {
                "title": "Settings",
                "separator": True,
                "items": [
                    {
                        "title": "Site settings",
                        "icon": "settings",
                        "link": reverse_lazy("admin:core_sitesettings_changelist"),
                    },
                    {
                        "title": "Telegram admins",
                        "icon": "send",
                        "link": reverse_lazy("admin:notifications_telegramadmin_changelist"),
                    },
                    {
                        "title": "Notifications",
                        "icon": "notifications",
                        "link": reverse_lazy("admin:notifications_notification_changelist"),
                    },
                ],
            },
        ],
    },
}

# ---------------------------------------------------------------------------
# Cache — used by django-ratelimit on the booking request form (5/hour/IP,
# CLAUDE.md §6). django-ratelimit wants a cache backend with atomic incr
# shared across processes (Memcached, or django-redis); CLAUDE.md §2
# explicitly rules out Redis/Celery and this project has no other reason to
# run Memcached, so we accept Django's default local-memory cache with its
# known limitation: gunicorn's 3 worker processes (docker-compose.yml) each
# keep their own counter, so the effective ceiling is closer to
# 5 x workers/hour/IP rather than a perfectly atomic 5/hour. Combined with
# the honeypot field this is an acceptable trade-off for a low-traffic
# booking form; revisit if spam becomes a real problem. E003 is silenced
# because it hard-fails `manage.py check`/`makemigrations` otherwise.
# ---------------------------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}
SILENCED_SYSTEM_CHECKS = ["django_ratelimit.E003"]

# ---------------------------------------------------------------------------
# django-ratelimit — used on the booking request form (5/hour/IP, CLAUDE.md §6)
# ---------------------------------------------------------------------------
RATELIMIT_VIEW = "apps.bookings.views.ratelimited_view"

# ---------------------------------------------------------------------------
# Telegram bot
# ---------------------------------------------------------------------------
TELEGRAM_BOT_TOKEN = env("TELEGRAM_BOT_TOKEN", default="")
TELEGRAM_WEBHOOK_SECRET = env("TELEGRAM_WEBHOOK_SECRET", default="change-me")
