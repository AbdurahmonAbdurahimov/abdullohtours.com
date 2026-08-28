from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from unfold.admin import ModelAdmin

from .models import BlogPost


@admin.register(BlogPost)
class BlogPostAdmin(TranslationAdmin, ModelAdmin):
    list_display = ("title", "status", "category", "author", "published_at", "translation_status")
    list_filter = ("status", "category")
    search_fields = ("title", "excerpt")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("related_destinations", "related_packages")

    @admin.display(description="Translations")
    def translation_status(self, obj):
        flags = {
            "RU": obj.translation_complete_ru,
            "DE": obj.translation_complete_de,
            "FR": obj.translation_complete_fr,
            "ES": obj.translation_complete_es,
        }
        return ", ".join(f"{code}✓" if done else f"{code}✗" for code, done in flags.items())
