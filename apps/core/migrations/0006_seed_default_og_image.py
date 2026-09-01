"""
Wire up the default OG image already sitting in media/seo/ (from the design
phase asset drop) to the SiteSettings singleton, same as 0002's contact
details — no image was ever set, so every page without its own og_image
fell back to nothing.
"""

from django.core.files.storage import default_storage
from django.db import migrations

DEFAULT_OG_IMAGE = "seo/screenshot.webp"


def seed_default_og_image(apps, schema_editor):
    if not default_storage.exists(DEFAULT_OG_IMAGE):
        return
    SiteSettings = apps.get_model("core", "SiteSettings")
    settings_obj = SiteSettings.objects.filter(pk=1).first()
    if settings_obj is None or settings_obj.default_og_image:
        return
    settings_obj.default_og_image = DEFAULT_OG_IMAGE
    settings_obj.default_og_image_width = 2400
    settings_obj.default_og_image_height = 1294
    settings_obj.save(
        update_fields=[
            "default_og_image",
            "default_og_image_width",
            "default_og_image_height",
        ]
    )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0005_sitesettings_default_og_image_height_and_more"),
    ]

    operations = [
        migrations.RunPython(seed_default_og_image, noop_reverse),
    ]
