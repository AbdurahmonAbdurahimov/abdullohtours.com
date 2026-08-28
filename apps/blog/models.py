from django.db import models

from apps.catalog.models import Destination, Package
from apps.core.models import SEOMixin


class BlogPost(SEOMixin):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        REVIEW = "REVIEW", "Review"
        PUBLISHED = "PUBLISHED", "Published"

    slug = models.SlugField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    excerpt = models.CharField(max_length=320, blank=True)
    body = models.TextField(blank=True, help_text="Rich text body (HTML).")
    cover_image = models.ImageField(upload_to="blog/", blank=True, null=True)
    author = models.CharField(max_length=255, blank=True)
    category = models.CharField(max_length=100, blank=True)
    related_destinations = models.ManyToManyField(
        Destination, blank=True, related_name="related_posts"
    )
    related_packages = models.ManyToManyField(Package, blank=True, related_name="related_posts")
    published_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)

    class Meta:
        ordering = ["-published_at"]

    def __str__(self) -> str:
        return self.title
