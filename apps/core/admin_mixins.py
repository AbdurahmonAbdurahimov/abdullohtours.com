from django.contrib import admin


class TranslationStatusMixin:
    """Adds a "Translations" column showing per-language completion flags
    (CLAUDE.md §11: "Content models show a per-language translation status
    column so gaps are visible"). Mix into any ModelAdmin whose model
    extends apps.core.models.SEOMixin.
    """

    def get_list_display(self, request):
        return (*super().get_list_display(request), "translation_status")

    @admin.display(description="Translations")
    def translation_status(self, obj):
        flags = {
            "RU": obj.translation_complete_ru,
            "DE": obj.translation_complete_de,
            "FR": obj.translation_complete_fr,
            "ES": obj.translation_complete_es,
            "AR": obj.translation_complete_ar,
        }
        return ", ".join(f"{code}✓" if done else f"{code}✗" for code, done in flags.items())
