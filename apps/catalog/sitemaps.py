from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.utils import translation

from .models import Destination, Package, RoutePage


class _I18nModelSitemap(Sitemap):
    """Base class that emits one sitemap entry per (object, active language).

    Keeps the per-language requirement from CLAUDE.md §7 honest without
    duplicating each sitemap class per language.
    """

    protocol = "https"

    def get_urls(self, *args, **kwargs):
        urls = []
        for lang_code, _label in settings.LANGUAGES:
            with translation.override(lang_code):
                urls.extend(super().get_urls(*args, **kwargs))
        return urls


class DestinationSitemap(_I18nModelSitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Destination.objects.filter(is_active=True)

    def lastmod(self, obj):
        return None

    def location(self, obj):
        from django.urls import reverse

        return reverse("catalog:destination_detail", kwargs={"slug": obj.slug})


class PackageSitemap(_I18nModelSitemap):
    changefreq = "weekly"
    priority = 0.9  # highest-value SEO pages per CLAUDE.md §6

    def items(self):
        return Package.objects.filter(is_active=True)

    def location(self, obj):
        from django.urls import reverse

        return reverse("catalog:package_detail", kwargs={"slug": obj.slug})


class RoutePageSitemap(_I18nModelSitemap):
    changefreq = "monthly"
    priority = 0.6  # programmatic long-tail pages — useful, not primary

    def items(self):
        return RoutePage.objects.filter(is_active=True)

    def lastmod(self, obj):
        return None

    def location(self, obj):
        from django.urls import reverse

        return reverse("catalog:route_detail", kwargs={"slug": obj.slug})
