from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.utils import translation

from .models import Car, Destination, Hotel, Package, RoutePage


class _I18nModelSitemap(Sitemap):
    """Base class that emits one sitemap entry per (object, active language)
    — but only for languages the object actually has a complete translation
    for (English always qualifies; every other language needs
    translation_complete_<lang>=True). Submitting /de/, /fr/, /es/, /ar/
    URLs that render the same "TODO: content needed" placeholder text as
    every other untranslated object is exactly the duplicate/thin content
    Google's guidance warns against — see
    https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls
    and apps/blog/sitemaps.py's BLOG_LANGUAGES, which restricts blog the
    same way. Keeps the per-language requirement from CLAUDE.md §7 honest
    without duplicating each sitemap class per language.
    """

    protocol = "https"
    _active_items = None

    def items(self):
        if self._active_items is not None:
            return self._active_items
        return self._all_items()

    def _all_items(self):  # pragma: no cover - overridden by subclasses
        raise NotImplementedError

    def get_urls(self, *args, **kwargs):
        all_items = list(self._all_items())
        urls = []
        for lang_code, _label in settings.LANGUAGES:
            if lang_code == "en":
                lang_items = all_items
            else:
                lang_items = [
                    obj
                    for obj in all_items
                    if getattr(obj, f"translation_complete_{lang_code}", False)
                ]
            if not lang_items:
                continue
            self._active_items = lang_items
            try:
                with translation.override(lang_code):
                    urls.extend(super().get_urls(*args, **kwargs))
            finally:
                self._active_items = None
        return urls


class DestinationSitemap(_I18nModelSitemap):
    changefreq = "weekly"
    priority = 0.8

    def _all_items(self):
        return Destination.objects.filter(is_active=True)

    def lastmod(self, obj):
        return None

    def location(self, obj):
        from django.urls import reverse

        return reverse("catalog:destination_detail", kwargs={"slug": obj.slug})


class PackageSitemap(_I18nModelSitemap):
    changefreq = "weekly"
    priority = 0.9  # highest-value SEO pages per CLAUDE.md §6

    def _all_items(self):
        return Package.objects.filter(is_active=True)

    def location(self, obj):
        from django.urls import reverse

        return reverse("catalog:package_detail", kwargs={"slug": obj.slug})


class RoutePageSitemap(_I18nModelSitemap):
    changefreq = "monthly"
    priority = 0.6  # programmatic long-tail pages — useful, not primary

    def _all_items(self):
        return RoutePage.objects.filter(is_active=True)

    def lastmod(self, obj):
        return None

    def location(self, obj):
        from django.urls import reverse

        return reverse("catalog:route_detail", kwargs={"slug": obj.slug})


class HotelSitemap(_I18nModelSitemap):
    changefreq = "weekly"
    priority = 0.6

    def _all_items(self):
        return Hotel.objects.filter(is_active=True)

    def lastmod(self, obj):
        return None

    def location(self, obj):
        from django.urls import reverse

        return reverse("catalog:hotel_detail", kwargs={"slug": obj.slug})


class CarSitemap(_I18nModelSitemap):
    changefreq = "weekly"
    priority = 0.6

    def _all_items(self):
        return Car.objects.filter(is_active=True)

    def lastmod(self, obj):
        return None

    def location(self, obj):
        from django.urls import reverse

        return reverse("catalog:car_detail", kwargs={"slug": obj.slug})
