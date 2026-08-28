"""
Seed the SiteSettings singleton with real contact details (CLAUDE.md §4).

Fields we don't have a confirmed real value for yet (email, office_address,
working_hours, response_time_promise) are left as clearly-marked
"TODO: confirm with Abdulloh" placeholders rather than invented values.
"""

from django.db import migrations


def seed_site_settings(apps, schema_editor):
    SiteSettings = apps.get_model("core", "SiteSettings")
    SiteSettings.objects.get_or_create(
        pk=1,
        defaults={
            "phone": "+998953336000",
            "whatsapp_number": "998953336000",
            "telegram_username": "abdulloh_talibdjanov",
            "instagram_username": "abdulloh_tours",
            "email": "TODO: confirm with Abdulloh",
            "office_address": "TODO: confirm with Abdulloh",
            "working_hours": "TODO: confirm with Abdulloh",
            "response_time_promise": "TODO: confirm with Abdulloh",
        },
    )


def unseed_site_settings(apps, schema_editor):
    SiteSettings = apps.get_model("core", "SiteSettings")
    SiteSettings.objects.filter(pk=1).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_site_settings, unseed_site_settings),
    ]
