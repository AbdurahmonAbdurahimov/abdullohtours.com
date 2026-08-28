"""
Phase 3 seed data (CLAUDE.md §13): programmatic SEO "destination pair"
landing pages (apps.catalog.models.RoutePage).

Generates every unordered pair from the active Destination rows — this is
deliberately the whole point of a *programmatic* SEO page: it scales with
the catalog rather than needing one of these hand-authored per pair.
Idempotent — safe to re-run.
"""

from __future__ import annotations

from itertools import combinations

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from apps.catalog.models import Destination, RoutePage

LANGUAGES = ("ru", "de", "fr", "es")


class Command(BaseCommand):
    help = "Seed RoutePage combinations for every pair of active destinations."

    def handle(self, *args, **options):
        destinations = list(Destination.objects.filter(is_active=True).order_by("order"))
        created_or_updated = 0

        for a, b in combinations(destinations, 2):
            slug = slugify(f"{a.name}-and-{b.name}")
            translation_flags = {
                f"translation_complete_{lang}": (
                    getattr(a, f"translation_complete_{lang}")
                    and getattr(b, f"translation_complete_{lang}")
                )
                for lang in LANGUAGES
            }
            RoutePage.objects.update_or_create(
                destination_a=a,
                destination_b=b,
                defaults={
                    "slug": slug,
                    "is_active": True,
                    "meta_title": f"{a.name} & {b.name} Tour | Abdulloh Tours",
                    "meta_description": (
                        f"Combine {a.name} and {b.name} in a single private tour, "
                        f"priced per vehicle with an English-speaking driver."
                    ),
                    **translation_flags,
                },
            )
            created_or_updated += 1

        self.stdout.write(self.style.SUCCESS(f"Seeded {created_or_updated} route pages."))
