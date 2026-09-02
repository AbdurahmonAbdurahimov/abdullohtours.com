"""
Seed the SiteSettings singleton's email with the real contact address,
same pattern as 0006's default_og_image backfill — the singleton row was
created before this address was known, so it's stuck at "" until backfilled.
"""

from django.db import migrations

DEFAULT_EMAIL = "info@abdullohtours.com"


def seed_default_email(apps, schema_editor):
    SiteSettings = apps.get_model("core", "SiteSettings")
    settings_obj = SiteSettings.objects.filter(pk=1).first()
    if settings_obj is None or settings_obj.email:
        return
    settings_obj.email = DEFAULT_EMAIL
    settings_obj.save(update_fields=["email"])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0006_seed_default_og_image"),
    ]

    operations = [
        migrations.RunPython(seed_default_email, noop_reverse),
    ]
