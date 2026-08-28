from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from unfold.admin import ModelAdmin

from apps.core.admin_mixins import TranslationStatusMixin

from .models import BlogPost


@admin.register(BlogPost)
class BlogPostAdmin(TranslationStatusMixin, TranslationAdmin, ModelAdmin):
    list_display = ("title", "status", "category", "author", "published_at")
    list_filter = ("status", "category")
    search_fields = ("title", "excerpt")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("related_destinations", "related_packages")
