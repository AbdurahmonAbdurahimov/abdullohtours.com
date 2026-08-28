from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    """Simple static-page section of the sitemap (home, about, faq, ...).

    One section per content type/app is assembled in config/urls.py; the
    per-language split comes from these URLs being generated for every
    active language via i18n_patterns + LANGUAGES.
    """

    priority = 0.6
    changefreq = "monthly"
    protocol = "https"

    def items(self):
        return ["core:home", "core:about", "core:reviews", "core:faq", "core:contact"]

    def location(self, item):
        return reverse(item)

    def get_urls(self, *args, **kwargs):
        # Emit one entry per active language, since these views live behind
        # i18n_patterns (language-prefixed URLs).
        urls = []
        for lang_code, _label in settings.LANGUAGES:
            from django.utils import translation

            with translation.override(lang_code):
                urls.extend(super().get_urls(*args, **kwargs))
        return urls
