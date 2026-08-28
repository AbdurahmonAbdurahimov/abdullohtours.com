from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import translation

from .models import BlogPost

# Blog is EN + RU only at launch (CLAUDE.md §12: "DE/FR/ES get tour and
# destination pages only"). blog_detail() doesn't gate by language, so
# without this the sitemap would advertise /de/, /fr/, /es/ blog URLs that
# render the same (untranslated) English body — exactly the duplicate
# content CLAUDE.md §7 warns against.
BLOG_LANGUAGES = ["en", "ru"]


class BlogPostSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5
    protocol = "https"

    def items(self):
        return BlogPost.objects.filter(status=BlogPost.Status.PUBLISHED)

    def lastmod(self, obj):
        return obj.published_at

    def location(self, obj):
        return reverse("blog:blog_detail", kwargs={"slug": obj.slug})

    def get_urls(self, *args, **kwargs):
        urls = []
        for lang_code in BLOG_LANGUAGES:
            with translation.override(lang_code):
                urls.extend(super().get_urls(*args, **kwargs))
        return urls
