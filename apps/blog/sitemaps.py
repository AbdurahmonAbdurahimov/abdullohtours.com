from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import translation

from .models import BlogPost


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
        for lang_code, _label in settings.LANGUAGES:
            with translation.override(lang_code):
                urls.extend(super().get_urls(*args, **kwargs))
        return urls
