from django.conf import settings

from apps.core.models import SiteSettings


def site_settings(request):
    """Expose the SiteSettings singleton + canonical host to every template.

    This is the ONLY sanctioned way templates should access contact details
    (phone / WhatsApp / Telegram / Instagram) — never hardcode them.
    """
    return {
        "site_settings": SiteSettings.load(),
        "CANONICAL_HOST": getattr(settings, "CANONICAL_HOST", ""),
    }
