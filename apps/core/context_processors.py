from django.conf import settings

from apps.core.models import SiteSettings

# Name of the cookie the light/dark toggle writes. Deliberately a cookie and
# not localStorage: CLAUDE.md §2 forbids localStorage/sessionStorage outright,
# and a cookie is readable server-side, which is what lets base.html stamp
# <html data-theme> during the initial render instead of after first paint
# (i.e. no flash of the wrong theme).
THEME_COOKIE_NAME = "theme"
VALID_THEMES = {"light", "dark"}


def site_settings(request):
    """Expose the SiteSettings singleton + canonical host to every template.

    This is the ONLY sanctioned way templates should access contact details
    (phone / WhatsApp / Telegram / Instagram) — never hardcode them.
    """
    return {
        "site_settings": SiteSettings.load(),
        "CANONICAL_HOST": getattr(settings, "CANONICAL_HOST", ""),
    }


def theme(request):
    """Expose the visitor's explicit light/dark choice, if they made one.

    Returns "" when no valid cookie is present, which base.html renders as a
    missing `data-theme` attribute — the CSS then falls back to the OS
    `prefers-color-scheme` (see static_src/input.css). An unrecognised cookie
    value is treated as "not set" rather than trusted, since it reaches us
    straight from the client.
    """
    value = request.COOKIES.get(THEME_COOKIE_NAME, "")
    return {"theme": value if value in VALID_THEMES else ""}
