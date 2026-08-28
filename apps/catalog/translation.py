from modeltranslation.translator import TranslationOptions, register

from .models import Activity, Destination, Package, PackageDay, RoutePage


@register(Destination)
class DestinationTranslationOptions(TranslationOptions):
    fields = ("name", "region", "intro", "body", "meta_title", "meta_description")


@register(Activity)
class ActivityTranslationOptions(TranslationOptions):
    fields = (
        "title",
        "short_desc",
        "full_desc",
        "included",
        "not_included",
        "meta_title",
        "meta_description",
    )


@register(Package)
class PackageTranslationOptions(TranslationOptions):
    fields = ("title", "summary", "body", "meta_title", "meta_description")


@register(PackageDay)
class PackageDayTranslationOptions(TranslationOptions):
    fields = ("title", "description")


@register(RoutePage)
class RoutePageTranslationOptions(TranslationOptions):
    # No free-text fields to translate — title is a derived property built
    # from the (already translated) destination names. Only the SEO meta
    # fields are real stored fields here.
    fields = ("meta_title", "meta_description")
