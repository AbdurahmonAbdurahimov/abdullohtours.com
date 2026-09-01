"""
Phase 1 seed data (CLAUDE.md §13): 5 destinations, 3 vehicle classes,
~15 activities, add-ons, and 3 packages.

Idempotent — safe to re-run. Every object is looked up by a stable natural
key (slug/name) and updated in place rather than duplicated.

Content note: intro/body/description copy below is original, factual travel
copy written for this seed pass — not scraped or paraphrased from Wikipedia
or any other source (CLAUDE.md §7/§3). It is deliberately plain and
information-dense rather than "brand voice" marketing copy: the home page
hero and About/Abdulloh's-bio copy remain explicit `TODO: content needed`
elsewhere because those specifically need Abdulloh's own voice, but
catalog/destination reference copy is normal, factual seed content and is
filled in here so Phase 1 has something real to browse and translate.
"""

from __future__ import annotations

from decimal import Decimal

from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from apps.catalog.models import (
    Activity,
    AddOn,
    Attraction,
    Destination,
    Driver,
    Package,
    PackageDay,
    PackageItem,
    Vehicle,
    VehicleClass,
)


class Command(BaseCommand):
    help = "Seed Phase 1 catalog data: destinations, vehicles, activities, add-ons, packages."

    def handle(self, *args, **options):
        destinations = self._seed_destinations()
        vehicle_classes = self._seed_vehicle_classes()
        self._seed_vehicles(vehicle_classes)
        self._seed_drivers()
        activities = self._seed_activities(destinations)
        addons = self._seed_addons()
        self._seed_packages(destinations, vehicle_classes, activities, addons)
        self.stdout.write(self.style.SUCCESS("Catalog seed complete."))

    # ------------------------------------------------------------------
    # Destinations + attractions
    # ------------------------------------------------------------------

    def _seed_destinations(self) -> dict[str, Destination]:
        data = [
            {
                "slug": "tashkent",
                "name": "Tashkent",
                "region": "Tashkent Region",
                "min_recommended_days": 1,
                "order": 1,
                "intro": (
                    "Uzbekistan's capital blends Soviet-era modernism with a restored old "
                    "city, wide tree-lined avenues and one of Central Asia's most decorated "
                    "metro systems."
                ),
                "body": (
                    "Most visitors land in Tashkent and use it as a first taste of the country "
                    "before heading to the Silk Road cities. The city was largely rebuilt after "
                    "a 1966 earthquake, which is why its centre feels distinctly Soviet-modernist "
                    "— broad boulevards, monumental squares and mosaic-covered public buildings.\n\n"
                    "Away from the government quarter, the Chorsu district keeps an older, "
                    "denser texture: a domed bazaar, narrow lanes and some of the city's oldest "
                    "surviving madrasahs. A day here pairs well with a ride on the metro itself, "
                    "where several stations were built as ornate public halls rather than plain "
                    "transit stops."
                ),
                "meta_title": "Tashkent Travel Guide | Abdulloh Tours",
                "meta_description": (
                    "Plan a private Tashkent city tour — Chorsu Bazaar, the ornate metro, "
                    "Independence Square — with an English-speaking driver."
                ),
                "attractions": [
                    (
                        "Chorsu Bazaar",
                        "A domed, multi-level market at the heart of the old city, selling "
                        "spices, dried fruit, bread and household goods much as it has for "
                        "generations.",
                        30,
                    ),
                    (
                        "Tashkent Metro",
                        "Opened in 1977, several stations were designed as decorated public "
                        "halls with marble, mosaics and chandeliers rather than plain transit "
                        "stops.",
                        60,
                    ),
                    (
                        "Independence Square",
                        "The city's largest public square, home to the Independence Monument "
                        "and a popular evening gathering spot for locals.",
                        45,
                    ),
                ],
            },
            {
                "slug": "samarkand",
                "name": "Samarkand",
                "region": "Samarkand Region",
                "min_recommended_days": 2,
                "order": 2,
                "intro": (
                    "One of the oldest continuously inhabited cities in Central Asia and the "
                    "former capital of Timur's empire, built around the monumental tiled "
                    "square of the Registan."
                ),
                "body": (
                    "Samarkand sat on the Silk Road between China and the Mediterranean for "
                    "over two thousand years, and its monuments reflect that: three vast, "
                    "tile-covered madrasahs facing each other across the Registan, the ribbed "
                    "blue dome of Timur's mausoleum at Gur-e-Amir, and the narrow, tomb-lined "
                    "avenue of Shah-i-Zinda climbing a hillside on the edge of the old city.\n\n"
                    "Most of what's on view dates from the 14th–15th century Timurid period, "
                    "when Samarkand was the capital of an empire stretching from India to "
                    "Anatolia. Two full days is a comfortable pace to see the major sites "
                    "without rushing between them."
                ),
                "meta_title": "Samarkand Tours | Abdulloh Tours",
                "meta_description": (
                    "Private Samarkand tours to the Registan, Gur-e-Amir and Shah-i-Zinda "
                    "with an English-speaking driver — priced per vehicle, not per person."
                ),
                "attractions": [
                    (
                        "Registan Square",
                        "Three monumental madrasahs (Ulugh Beg, Sher-Dor and Tilya-Kori) "
                        "facing each other across a public square, the centrepiece of "
                        "Timurid Samarkand.",
                        90,
                    ),
                    (
                        "Gur-e-Amir Mausoleum",
                        "The ribbed turquoise dome marks the tomb of Timur (Tamerlane) and "
                        "several of his descendants, including Ulugh Beg.",
                        45,
                    ),
                    (
                        "Shah-i-Zinda",
                        "A narrow avenue of blue-tiled mausoleums built up over several "
                        "centuries, climbing a hillside just outside the old city walls.",
                        60,
                    ),
                ],
            },
            {
                "slug": "bukhara",
                "name": "Bukhara",
                "region": "Bukhara Region",
                "min_recommended_days": 2,
                "order": 3,
                "intro": (
                    "A former centre of Islamic scholarship with an old city small enough to "
                    "walk end to end, its skyline still dominated by a 47-metre 12th-century "
                    "minaret."
                ),
                "body": (
                    "Where Samarkand's monuments are spread across a modern city, Bukhara's "
                    "historic core survives largely intact and walkable — the Po-i-Kalyan "
                    "complex, the Ark fortress, and a scatter of trading domes and madrasahs "
                    "within a few hundred metres of each other around the Lyab-i Hauz pool.\n\n"
                    "Bukhara was a major centre of Islamic learning for centuries, and that "
                    "history is visible in the sheer density of madrasahs packed into a "
                    "compact old town. It's an easier city to see on foot than Samarkand, "
                    "which makes it a good second stop after a more spread-out first day."
                ),
                "meta_title": "Bukhara Tours | Abdulloh Tours",
                "meta_description": (
                    "Walk Bukhara's old city with a private driver — Po-i-Kalyan, the Ark "
                    "fortress and Lyab-i Hauz — on your own schedule."
                ),
                "attractions": [
                    (
                        "Po-i-Kalyan Complex",
                        "A minaret, mosque and madrasah grouped together at the historic "
                        "centre of Bukhara; the 47-metre Kalyan Minaret dates to 1127.",
                        60,
                    ),
                    (
                        "Ark Fortress",
                        "A fortified royal residence occupied from the 5th century until "
                        "1920, now housing several small museums.",
                        60,
                    ),
                    (
                        "Lyab-i Hauz",
                        "A 17th-century pool surrounded by mulberry trees, madrasahs and "
                        "tea houses — the social centre of the old city.",
                        30,
                    ),
                ],
            },
            {
                "slug": "khiva",
                "name": "Khiva",
                "region": "Khorezm Region",
                "min_recommended_days": 1,
                "order": 4,
                "intro": (
                    "A walled desert city where the entire old town, Itchan Kala, is "
                    "preserved as a single open-air site — the most complete example of a "
                    "Central Asian mud-brick city."
                ),
                "body": (
                    "Khiva is the furthest of the classic Silk Road stops, out in the "
                    "Khorezm oasis near the Turkmenistan border, which keeps it quieter than "
                    "Samarkand or Bukhara. Its old town, Itchan Kala, is fully walled and "
                    "small enough to cross in twenty minutes — but densely packed with "
                    "madrasahs, minarets and the unfinished, oddly stout Kalta Minor.\n\n"
                    "Because the whole old city is a protected site with a single entrance "
                    "ticket, Khiva works well as a full but compact day: arrive, see the "
                    "walled city properly, and move on the same evening or next morning."
                ),
                "meta_title": "Khiva Tours | Abdulloh Tours",
                "meta_description": (
                    "Visit Khiva's walled old city, Itchan Kala, with a private "
                    "English-speaking driver — the most complete Silk Road old town in "
                    "Uzbekistan."
                ),
                "attractions": [
                    (
                        "Itchan Kala",
                        "The walled inner city of Khiva, preserved in its entirety as a "
                        "single open-air museum of Khorezm architecture.",
                        120,
                    ),
                    (
                        "Kalta Minor Minaret",
                        "A wide, turquoise-tiled minaret left unfinished in 1855 — intended "
                        "to be the tallest in Central Asia.",
                        20,
                    ),
                    (
                        "Kunya-Ark",
                        "The old khan's fortress and residence, built into the western wall "
                        "of Itchan Kala.",
                        45,
                    ),
                ],
            },
            {
                "slug": "amirsoy-chimgan",
                "name": "Amirsoy & Chimgan",
                "region": "Tashkent Region (Chimgan Mountains)",
                "min_recommended_days": 1,
                "order": 5,
                "intro": (
                    "A mountain day trip from Tashkent — a modern ski/summer resort at "
                    "Amirsoy, the older Chimgan ridge behind it, and the Charvak reservoir "
                    "below."
                ),
                "body": (
                    "About 90 minutes from Tashkent, the Chimgan mountains are the capital's "
                    "easiest escape from the heat: a cable car at Amirsoy runs year-round, "
                    "hiking trails cross the Chimgan ridge in summer, and the turquoise "
                    "Charvak reservoir sits in the valley below.\n\n"
                    "This works well as a single long day trip out of Tashkent, or as a first "
                    "or last stop bookending a longer Silk Road itinerary — it needs no "
                    "overnight stay for most visitors."
                ),
                "meta_title": "Amirsoy & Chimgan Mountain Day Trip | Abdulloh Tours",
                "meta_description": (
                    "Private day trip from Tashkent to Amirsoy and Chimgan — cable car, "
                    "hiking and the Charvak reservoir."
                ),
                "attractions": [
                    (
                        "Amirsoy Cable Car",
                        "A modern gondola climbing the Amirsoy resort, running through both "
                        "the winter ski season and summer.",
                        90,
                    ),
                    (
                        "Charvak Reservoir",
                        "A turquoise reservoir in the valley below Chimgan, popular for boat "
                        "trips and lakeside views.",
                        60,
                    ),
                    (
                        "Chimgan Ridge Trails",
                        "Hiking routes along the older Chimgan ridge, with views back down "
                        "over the Charvak reservoir.",
                        120,
                    ),
                ],
            },
        ]

        # Media already sitting in media/ from the design phase (CLAUDE.md
        # §7 image pipeline) — wired up by natural key rather than uploaded
        # again, since default_storage already has these committed files.
        # Attraction.images stores full URLs (help_text: "paths/URLs"), not
        # bare storage names — the template renders it straight into <img
        # src> with no MEDIA_URL prefix, so a bare name 404s.
        attraction_images = {
            "Registan Square": [default_storage.url("attractions/topattractions-registan.webp")],
            "Gur-e-Amir Mausoleum": [default_storage.url("attractions/topattractions-guremir.webp")],
        }

        destinations: dict[str, Destination] = {}
        for row in data:
            attractions = row.pop("attractions")
            hero_image = f"destinations/{row['slug']}-hero.webp"
            if default_storage.exists(hero_image):
                row["hero_image"] = hero_image
            obj, _created = Destination.objects.update_or_create(
                slug=row["slug"],
                defaults={**row, "is_active": True},
            )
            for name, description, duration in attractions:
                defaults = {"description": description, "typical_duration_min": duration}
                if name in attraction_images:
                    defaults["images"] = attraction_images[name]
                Attraction.objects.update_or_create(
                    destination=obj,
                    name=name,
                    defaults=defaults,
                )
            destinations[row["slug"]] = obj
        return destinations

    # ------------------------------------------------------------------
    # Fleet
    # ------------------------------------------------------------------

    def _seed_vehicle_classes(self) -> dict[str, VehicleClass]:
        data = [
            ("Sedan", 1, 3, Decimal("50"), 1),
            ("Minivan", 4, 7, Decimal("80"), 2),
            ("Minibus", 8, 15, Decimal("120"), 3),
        ]
        classes: dict[str, VehicleClass] = {}
        for name, min_pax, max_pax, rate, order in data:
            obj, _ = VehicleClass.objects.update_or_create(
                name=name,
                defaults={
                    "min_pax": min_pax,
                    "max_pax": max_pax,
                    "daily_rate_usd": rate,
                    "order": order,
                },
            )
            classes[name] = obj
        return classes

    def _seed_vehicles(self, vehicle_classes: dict[str, VehicleClass]) -> None:
        data = [
            ("Sedan #1", "Sedan", Decimal("25")),
            ("Sedan #2", "Sedan", Decimal("25")),
            ("Minivan #1", "Minivan", Decimal("40")),
            ("Minibus #1", "Minibus", Decimal("60")),
        ]
        for name, class_name, cost in data:
            Vehicle.objects.update_or_create(
                name=name,
                defaults={
                    "vehicle_class": vehicle_classes[class_name],
                    "is_active": True,
                    "daily_cost_usd": cost,
                },
            )

    def _seed_drivers(self) -> None:
        data = [
            ("Sardor Umarov", "English, Uzbek, Russian"),
            ("Jasur Karimov", "English, Uzbek, Russian"),
        ]
        for name, languages in data:
            Driver.objects.update_or_create(
                name=name, defaults={"languages": languages, "is_active": True}
            )

    # ------------------------------------------------------------------
    # Activities + add-ons
    # ------------------------------------------------------------------

    def _seed_activities(self, destinations: dict[str, Destination]) -> dict[str, Activity]:
        data = [
            (
                "tashkent",
                "Chorsu Bazaar Food Tour",
                Activity.PriceType.PER_PERSON,
                Decimal("25"),
                2,
                "A guided walk through Tashkent's largest bazaar, tasting bread, dried "
                "fruit and local snacks along the way.",
            ),
            (
                "tashkent",
                "Tashkent City Highlights",
                Activity.PriceType.PER_VEHICLE,
                Decimal("40"),
                3,
                "A half-day loop past Independence Square, the Amir Timur Museum and the "
                "old city around Chorsu.",
            ),
            (
                "tashkent",
                "Tashkent Metro Art Tour",
                Activity.PriceType.PER_PERSON,
                Decimal("15"),
                1.5,
                "A ride between the metro's most ornately decorated stations, each built "
                "to a different design theme.",
            ),
            (
                "samarkand",
                "Registan Square Entrance",
                Activity.PriceType.PER_PERSON,
                Decimal("10"),
                1.5,
                "Entrance to Samarkand's three-madrasah Registan complex, with time to "
                "see the interior courtyards.",
            ),
            (
                "samarkand",
                "Gur-e-Amir Mausoleum Entrance",
                Activity.PriceType.PER_PERSON,
                Decimal("5"),
                1,
                "Entrance to Timur's mausoleum and its ribbed turquoise dome.",
            ),
            (
                "samarkand",
                "Silk Paper Workshop Visit",
                Activity.PriceType.PER_PERSON,
                Decimal("12"),
                1.5,
                "A working paper mill outside Samarkand demonstrating the traditional "
                "mulberry-bark paper process, with a small shop on site.",
            ),
            (
                "bukhara",
                "Ark Fortress Entrance",
                Activity.PriceType.PER_PERSON,
                Decimal("6"),
                1,
                "Entrance to the Ark, Bukhara's former royal fortress and residence.",
            ),
            (
                "bukhara",
                "Po-i-Kalyan Complex Tour",
                Activity.PriceType.PER_PERSON,
                Decimal("8"),
                1.5,
                "A guided visit to the minaret, mosque and madrasah at the historic "
                "centre of Bukhara.",
            ),
            (
                "bukhara",
                "Traditional Carpet Workshop",
                Activity.PriceType.PER_PERSON,
                Decimal("10"),
                1,
                "A small family workshop demonstrating hand-knotted silk and wool carpet "
                "weaving.",
            ),
            (
                "khiva",
                "Itchan Kala All-in-One Ticket",
                Activity.PriceType.PER_PERSON,
                Decimal("12"),
                3,
                "A single ticket covering every monument inside Khiva's walled old city.",
            ),
            (
                "khiva",
                "Kalta Minor Viewpoint",
                Activity.PriceType.PER_PERSON,
                Decimal("4"),
                0.5,
                "Access to a nearby viewpoint over the unfinished, turquoise-tiled Kalta "
                "Minor minaret.",
            ),
            (
                "khiva",
                "Sunset Photography Walk",
                Activity.PriceType.PER_VEHICLE,
                Decimal("30"),
                2,
                "A late-afternoon walk timed for the old city's walls and minarets in "
                "golden-hour light.",
            ),
            (
                "amirsoy-chimgan",
                "Amirsoy Cable Car Day Pass",
                Activity.PriceType.PER_PERSON,
                Decimal("35"),
                3,
                "A full-day pass for the Amirsoy gondola, running year-round over the "
                "resort's slopes.",
            ),
            (
                "amirsoy-chimgan",
                "Chimgan Mountain Hike",
                Activity.PriceType.PER_PERSON,
                Decimal("20"),
                4,
                "A guided hike along the Chimgan ridge, with views over the Charvak " "reservoir.",
            ),
            (
                "amirsoy-chimgan",
                "Charvak Lake Boat Trip",
                Activity.PriceType.PER_PERSON,
                Decimal("25"),
                1.5,
                "A short boat trip out on the Charvak reservoir below Chimgan.",
            ),
        ]

        activities: dict[str, Activity] = {}
        for dest_slug, title, price_type, price, duration, short_desc in data:
            slug = slugify(title)
            obj, _ = Activity.objects.update_or_create(
                slug=slug,
                defaults={
                    "destination": destinations[dest_slug],
                    "title": title,
                    "price_type": price_type,
                    "base_price_usd": price,
                    "duration_hours": Decimal(str(duration)),
                    "short_desc": short_desc,
                    "full_desc": short_desc,
                    "is_active": True,
                },
            )
            activities[slug] = obj
        return activities

    def _seed_addons(self) -> dict[str, AddOn]:
        data = [
            (
                "English-Speaking Guide",
                "A licensed local guide accompanying your vehicle for the day, on top of "
                "the driver.",
                Decimal("50"),
                AddOn.Unit.PER_DAY,
            ),
            (
                "Hotel (3-Star, Double Room)",
                "A double room in a centrally located 3-star hotel, booked on your behalf.",
                Decimal("60"),
                AddOn.Unit.PER_NIGHT,
            ),
            (
                "Airport VIP Meet & Greet",
                "Fast-track arrival assistance and a private transfer from Tashkent "
                "International Airport.",
                Decimal("80"),
                AddOn.Unit.PER_GROUP,
            ),
        ]
        addons: dict[str, AddOn] = {}
        for name, description, price, unit in data:
            obj, _ = AddOn.objects.update_or_create(
                name=name,
                defaults={"description": description, "price_usd": price, "unit": unit},
            )
            addons[name] = obj
        return addons

    # ------------------------------------------------------------------
    # Packages
    # ------------------------------------------------------------------

    def _seed_packages(
        self,
        destinations: dict[str, Destination],
        vehicle_classes: dict[str, VehicleClass],
        activities: dict[str, Activity],
        addons: dict[str, AddOn],
    ) -> None:
        guide = addons["English-Speaking Guide"]
        hotel = addons["Hotel (3-Star, Double Room)"]

        packages = [
            {
                "slug": "silk-road-highlights",
                "title": "Silk Road Highlights",
                "tier": Package.Tier.ECONOMY,
                "total_days": 5,
                "vehicle_class": "Sedan",
                "summary": (
                    "Tashkent, Samarkand and Bukhara in five days — the fastest way to see "
                    "Uzbekistan's three best-known Silk Road cities."
                ),
                "body": (
                    "A compact route for a first visit: one day in Tashkent, two in "
                    "Samarkand, two in Bukhara, covering the Registan, Gur-e-Amir, "
                    "Shah-i-Zinda, the Po-i-Kalyan complex and the Ark fortress."
                ),
                "days": [
                    (
                        1,
                        "Arrival & Tashkent",
                        "Airport pickup, hotel check-in, and a half-day city tour covering "
                        "Independence Square and Chorsu Bazaar.",
                        ["Tashkent City Highlights", "Chorsu Bazaar Food Tour"],
                    ),
                    (
                        2,
                        "Travel to Samarkand",
                        "Morning drive to Samarkand, afternoon at the Registan and "
                        "Shah-i-Zinda.",
                        ["Registan Square Entrance"],
                    ),
                    (
                        3,
                        "Samarkand in full",
                        "Gur-e-Amir, the Ulugh Beg Observatory ruins, and a silk paper "
                        "workshop outside the city.",
                        ["Gur-e-Amir Mausoleum Entrance", "Silk Paper Workshop Visit"],
                    ),
                    (
                        4,
                        "Travel to Bukhara",
                        "Drive to Bukhara, afternoon walk around Lyab-i Hauz and the "
                        "Po-i-Kalyan complex.",
                        ["Po-i-Kalyan Complex Tour"],
                    ),
                    (
                        5,
                        "Bukhara & departure",
                        "The Ark fortress and a carpet workshop before transfer to the "
                        "airport or onward train.",
                        ["Ark Fortress Entrance", "Traditional Carpet Workshop"],
                    ),
                ],
            },
            {
                "slug": "classic-uzbekistan",
                "title": "Classic Uzbekistan",
                "tier": Package.Tier.STANDARD,
                "total_days": 8,
                "vehicle_class": "Minivan",
                "summary": (
                    "The full classic route — Tashkent, Samarkand, Bukhara and Khiva — with "
                    "a guide included and more time at each stop."
                ),
                "body": (
                    "An eight-day itinerary that adds Khiva to the classic three-city route, "
                    "with a professional guide included throughout rather than just a "
                    "driver, and an extra day built in for a slower pace through Samarkand "
                    "and Bukhara."
                ),
                "days": [
                    (
                        1,
                        "Arrival & Tashkent",
                        "Airport pickup and a full city tour of Tashkent.",
                        ["Tashkent City Highlights", "Tashkent Metro Art Tour"],
                    ),
                    (
                        2,
                        "Travel to Samarkand",
                        "Drive to Samarkand, afternoon at the Registan.",
                        ["Registan Square Entrance"],
                    ),
                    (
                        3,
                        "Samarkand in full",
                        "Gur-e-Amir, Shah-i-Zinda and a silk paper workshop.",
                        ["Gur-e-Amir Mausoleum Entrance", "Silk Paper Workshop Visit"],
                    ),
                    (
                        4,
                        "Travel to Bukhara",
                        "Drive to Bukhara, evening at Lyab-i Hauz.",
                        [],
                    ),
                    (
                        5,
                        "Bukhara in full",
                        "Po-i-Kalyan complex, the Ark fortress, and a carpet workshop.",
                        [
                            "Po-i-Kalyan Complex Tour",
                            "Ark Fortress Entrance",
                            "Traditional Carpet Workshop",
                        ],
                    ),
                    (
                        6,
                        "Travel to Khiva",
                        "A longer drive across the desert to Khiva, arriving by evening.",
                        [],
                    ),
                    (
                        7,
                        "Khiva in full",
                        "A full day inside the walled old city of Itchan Kala.",
                        ["Itchan Kala All-in-One Ticket", "Sunset Photography Walk"],
                    ),
                    (
                        8,
                        "Departure",
                        "Flight or onward transfer from Urgench airport, near Khiva.",
                        [],
                    ),
                ],
            },
            {
                "slug": "grand-uzbekistan-mountains",
                "title": "Grand Uzbekistan & Mountains",
                "tier": Package.Tier.PREMIUM,
                "total_days": 10,
                "vehicle_class": "Minivan",
                "summary": (
                    "All five destinations — the four Silk Road cities plus a mountain day "
                    "at Amirsoy and Chimgan — with guide and hotels included."
                ),
                "body": (
                    "The complete route: Tashkent, Samarkand, Bukhara and Khiva as in the "
                    "Classic itinerary, opened with a mountain day trip to Amirsoy and "
                    "Chimgan before heading out on the Silk Road cities. Guide and hotel "
                    "add-ons are bundled in rather than optional."
                ),
                "days": [
                    (
                        1,
                        "Arrival & Tashkent",
                        "Airport VIP meet & greet, hotel check-in, evening city walk.",
                        [],
                    ),
                    (
                        2,
                        "Amirsoy & Chimgan day trip",
                        "A full day in the mountains: cable car, a Chimgan ridge hike, and "
                        "the Charvak reservoir.",
                        [
                            "Amirsoy Cable Car Day Pass",
                            "Chimgan Mountain Hike",
                            "Charvak Lake Boat Trip",
                        ],
                    ),
                    (
                        3,
                        "Tashkent city tour",
                        "Chorsu Bazaar, Independence Square and the metro's decorated " "stations.",
                        ["Tashkent City Highlights", "Chorsu Bazaar Food Tour"],
                    ),
                    (
                        4,
                        "Travel to Samarkand",
                        "Drive to Samarkand, afternoon at the Registan.",
                        ["Registan Square Entrance"],
                    ),
                    (
                        5,
                        "Samarkand in full",
                        "Gur-e-Amir, Shah-i-Zinda and a silk paper workshop.",
                        ["Gur-e-Amir Mausoleum Entrance", "Silk Paper Workshop Visit"],
                    ),
                    (
                        6,
                        "Travel to Bukhara",
                        "Drive to Bukhara, evening at Lyab-i Hauz.",
                        [],
                    ),
                    (
                        7,
                        "Bukhara in full",
                        "Po-i-Kalyan complex, the Ark fortress and a carpet workshop.",
                        [
                            "Po-i-Kalyan Complex Tour",
                            "Ark Fortress Entrance",
                            "Traditional Carpet Workshop",
                        ],
                    ),
                    (
                        8,
                        "Travel to Khiva",
                        "A longer drive across the desert to Khiva.",
                        [],
                    ),
                    (
                        9,
                        "Khiva in full",
                        "A full day inside Itchan Kala, timed to end with sunset light on "
                        "the walls.",
                        ["Itchan Kala All-in-One Ticket", "Sunset Photography Walk"],
                    ),
                    (
                        10,
                        "Departure",
                        "Flight or onward transfer from Urgench airport.",
                        [],
                    ),
                ],
            },
        ]

        gallery_images = [
            "packages/gallery/visualjourneys-1.webp",
            "packages/gallery/visualjourneys-2.webp",
            "packages/gallery/visualjourneys-3.webp",
        ]

        for pkg_data in packages:
            days = pkg_data.pop("days")
            vehicle_class_name = pkg_data.pop("vehicle_class")
            hero_image = f"packages/{pkg_data['slug']}-hero.webp"
            if default_storage.exists(hero_image):
                pkg_data["hero_image"] = hero_image
            is_featured = pkg_data["tier"] == Package.Tier.STANDARD
            if is_featured and all(default_storage.exists(p) for p in gallery_images):
                pkg_data["gallery"] = gallery_images
            package, _ = Package.objects.update_or_create(
                slug=pkg_data["slug"],
                defaults={
                    **pkg_data,
                    "base_vehicle_class": vehicle_classes[vehicle_class_name],
                    "is_active": True,
                    "is_featured": is_featured,
                },
            )
            for day_number, title, description, activity_titles in days:
                day, _ = PackageDay.objects.update_or_create(
                    package=package,
                    day_number=day_number,
                    defaults={"title": title, "description": description},
                )
                PackageItem.objects.filter(package_day=day).delete()
                for activity_title in activity_titles:
                    slug = slugify(activity_title)
                    PackageItem.objects.create(
                        package_day=day, activity=activities[slug], is_optional=False
                    )
                if package.tier in (Package.Tier.STANDARD, Package.Tier.PREMIUM):
                    PackageItem.objects.create(package_day=day, addon=guide, is_optional=False)
                    if day_number < package.total_days:
                        PackageItem.objects.create(package_day=day, addon=hotel, is_optional=False)
