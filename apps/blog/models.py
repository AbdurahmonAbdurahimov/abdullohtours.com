from django.db import models
from django.urls import reverse
from django.utils import translation

from apps.catalog.models import Destination, Package
from apps.core.fields import WebPImageField
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
    cover_image = WebPImageField(
        upload_to="blog/",
        blank=True,
        null=True,
        width_field="cover_image_width",
        height_field="cover_image_height",
    )
    cover_image_width = models.PositiveIntegerField(null=True, blank=True, editable=False)
    cover_image_height = models.PositiveIntegerField(null=True, blank=True, editable=False)
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

    def get_absolute_url(self) -> str:
        with translation.override("en"):
            return reverse("blog:blog_detail", kwargs={"slug": self.slug})
