"""
Root URLconf.

Page URLs live behind i18n_patterns with prefix_default_language=True, so
even English gets a /en/ prefix (CLAUDE.md §6: "Language prefix on every
URL. en is default and x-default"). /sitemap.xml, /robots.txt and the
Telegram webhook are intentionally NOT language-prefixed.
"""

from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from apps.blog.sitemaps import BlogPostSitemap
from apps.catalog.sitemaps import DestinationSitemap, PackageSitemap
from apps.core.sitemaps import StaticViewSitemap
from apps.core.views import robots_txt

# One section per content type (CLAUDE.md §7: "django.contrib.sitemaps with
# separate sections per content type and per language" — the per-language
# split happens inside each Sitemap subclass, see apps/*/sitemaps.py).
sitemaps = {
    "static": StaticViewSitemap,
    "destinations": DestinationSitemap,
    "packages": PackageSitemap,
    "blog": BlogPostSitemap,
}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("robots.txt", robots_txt, name="robots_txt"),
    path("", include("apps.notifications.urls")),  # /tg/webhook/<secret>/
    path("i18n/", include("django.conf.urls.i18n")),  # set_language, used by the language switcher
]

urlpatterns += i18n_patterns(
    path("", include("apps.core.urls")),
    path("", include("apps.catalog.urls")),
    path("", include("apps.bookings.urls")),
    path("blog/", include("apps.blog.urls")),
    prefix_default_language=True,
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR / "static")
