"""Seed browsable Car rows for the Minivan and Minibus vehicle classes.

Only a single Sedan car was ever seeded, so the Tour Builder's "Vehicle"
step (templates/catalog/tour_builder.html, step 1) only ever rendered one
selectable card — larger groups had nothing to pick from. VehicleClass
already had Minivan/Minibus tiers (apps.catalog.pricing prices off those
regardless of which Car is picked), they just had no matching Car listing.
"""

from django.db import migrations


def seed_larger_cars(apps, schema_editor):
    Car = apps.get_model("catalog", "Car")
    VehicleClass = apps.get_model("catalog", "VehicleClass")

    def vehicle_class(name):
        return VehicleClass.objects.filter(name=name).order_by("max_pax").first()

    minivan = vehicle_class("Minivan")
    minibus = vehicle_class("Minibus")

    if minivan is not None:
        Car.objects.get_or_create(
            slug="minivan",
            defaults={
                # apps.get_model() returns the historical model without
                # django-modeltranslation's "name" -> "name_en" proxying,
                # so the translated column must be set directly or it
                # saves blank.
                "name_en": "Minivan",
                "category": "MINIVAN",
                "vehicle_class": minivan,
                "capacity_pax": minivan.max_pax,
                "daily_rate_usd": minivan.daily_rate_usd,
                "is_active": True,
                "order": 1,
            },
        )

    if minibus is not None:
        Car.objects.get_or_create(
            slug="minibus",
            defaults={
                "name_en": "Minibus",
                "category": "MINIBUS",
                "vehicle_class": minibus,
                "capacity_pax": minibus.max_pax,
                "daily_rate_usd": minibus.daily_rate_usd,
                "is_active": True,
                "order": 2,
            },
        )


def unseed_larger_cars(apps, schema_editor):
    Car = apps.get_model("catalog", "Car")
    Car.objects.filter(slug__in=["minivan", "minibus"]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0007_remove_activity_images_remove_attraction_images_and_more"),
    ]

    operations = [
        migrations.RunPython(seed_larger_cars, unseed_larger_cars),
    ]
