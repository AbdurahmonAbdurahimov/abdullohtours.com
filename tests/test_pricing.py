"""
Unit tests for apps/catalog/pricing.py — the pricing engine.

CLAUDE.md's working agreement is explicit: write tests for the pricing
engine before anything else touches it, and this file must pass before the
rest of the build proceeds. Everything here operates on plain dataclasses,
no database required.
"""

from datetime import date
from decimal import Decimal

import pytest

from apps.catalog.pricing import (
    CHILD_ENTRANCE_FARE_WEIGHT,
    ActivitySelection,
    AddOnSelection,
    AddOnUnit,
    PriceType,
    QuoteRequest,
    VehicleClassOption,
    calculate_quote,
    resolve_seasonal_multiplier,
    select_vehicle,
    weighted_pax,
)

SEDAN = VehicleClassOption(id=1, name="Sedan", max_pax=3, daily_rate_usd=Decimal("50"))
MINIVAN = VehicleClassOption(id=2, name="Minivan", max_pax=8, daily_rate_usd=Decimal("90"))
BUS = VehicleClassOption(id=3, name="Bus", max_pax=16, daily_rate_usd=Decimal("150"))

ALL_CLASSES = [SEDAN, MINIVAN, BUS]


# ---------------------------------------------------------------------------
# Vehicle selection
# ---------------------------------------------------------------------------


def test_single_vehicle_fits_group():
    vehicle_class, vehicle_count = select_vehicle(ALL_CLASSES, adults=2, children=0)
    assert vehicle_class == SEDAN
    assert vehicle_count == 1


def test_group_exactly_fills_a_class():
    vehicle_class, vehicle_count = select_vehicle(ALL_CLASSES, adults=8, children=0)
    assert vehicle_class == MINIVAN
    assert vehicle_count == 1


def test_overflow_triggers_second_vehicle_of_largest_class():
    # 20 pax > largest class (Bus, max_pax=16) -> falls back to Bus x2.
    vehicle_class, vehicle_count = select_vehicle(ALL_CLASSES, adults=20, children=0)
    assert vehicle_class == BUS
    assert vehicle_count == 2


def test_overflow_transport_cost_is_multiplied_by_vehicle_count():
    req = QuoteRequest(start_date=date(2026, 5, 1), days=3, adults=20, children=0)
    quote = calculate_quote(req, ALL_CLASSES)
    assert quote["vehicle_count"] == 2
    transport = quote["line_items"][0]
    assert transport["type"] == "TRANSPORT"
    # 3 days * 2 vehicles * $150/day = $900
    assert transport["subtotal"] == Decimal("900")
    assert quote["subtotal_usd"] == Decimal("900")


def test_children_count_fully_toward_vehicle_capacity():
    # 2 adults + 2 children = 4 pax -> needs Minivan, not Sedan (max 3).
    vehicle_class, vehicle_count = select_vehicle(ALL_CLASSES, adults=2, children=2)
    assert vehicle_class == MINIVAN
    assert vehicle_count == 1


def test_manual_upgrade_is_honored():
    vehicle_class, _ = select_vehicle(
        ALL_CLASSES, adults=2, children=0, manual_vehicle_class_id=MINIVAN.id
    )
    assert vehicle_class == MINIVAN


def test_manual_downgrade_below_required_capacity_is_rejected():
    # 5 pax requires Minivan; requesting Sedan (max 3) must be ignored.
    vehicle_class, vehicle_count = select_vehicle(
        ALL_CLASSES, adults=5, children=0, manual_vehicle_class_id=SEDAN.id
    )
    assert vehicle_class == MINIVAN
    assert vehicle_count == 1


# ---------------------------------------------------------------------------
# Per-item pricing math
# ---------------------------------------------------------------------------


def test_per_vehicle_activity_is_flat_per_group_not_per_person():
    req = QuoteRequest(
        start_date=date(2026, 5, 1),
        days=1,
        adults=4,
        children=0,
        activities=[
            ActivitySelection(
                label="Private guided city tour",
                price_type=PriceType.PER_VEHICLE,
                unit_price_usd=Decimal("40"),
            )
        ],
    )
    quote = calculate_quote(req, ALL_CLASSES)
    activity_line = next(li for li in quote["line_items"] if li["type"] == "ACTIVITY")
    assert activity_line["subtotal"] == Decimal("40")
    assert activity_line["qty"] == Decimal("1")


def test_per_person_activity_scales_with_adults():
    req = QuoteRequest(
        start_date=date(2026, 5, 1),
        days=1,
        adults=4,
        children=0,
        activities=[
            ActivitySelection(
                label="Registan entrance",
                price_type=PriceType.PER_PERSON,
                unit_price_usd=Decimal("10"),
                is_entrance_fee=True,
            )
        ],
    )
    quote = calculate_quote(req, ALL_CLASSES)
    activity_line = next(li for li in quote["line_items"] if li["type"] == "ACTIVITY")
    assert activity_line["subtotal"] == Decimal("40")


def test_per_day_addon_scales_with_days():
    req = QuoteRequest(
        start_date=date(2026, 5, 1),
        days=5,
        adults=2,
        children=0,
        addons=[
            AddOnSelection(
                label="English guide", unit=AddOnUnit.PER_DAY, unit_price_usd=Decimal("50")
            )
        ],
    )
    quote = calculate_quote(req, ALL_CLASSES)
    addon_line = next(li for li in quote["line_items"] if li["type"] == "ADDON")
    assert addon_line["subtotal"] == Decimal("250")


def test_per_night_addon_scales_with_pax_and_nights():
    # 5 days -> defaults to 4 nights; 3 pax * $60/night * 4 nights = $720.
    req = QuoteRequest(
        start_date=date(2026, 5, 1),
        days=5,
        adults=3,
        children=0,
        addons=[
            AddOnSelection(label="Hotel", unit=AddOnUnit.PER_NIGHT, unit_price_usd=Decimal("60"))
        ],
    )
    quote = calculate_quote(req, ALL_CLASSES)
    addon_line = next(li for li in quote["line_items"] if li["type"] == "ADDON")
    assert req.resolved_nights == 4
    assert addon_line["subtotal"] == Decimal("720")


def test_per_group_addon_is_flat():
    req = QuoteRequest(
        start_date=date(2026, 5, 1),
        days=1,
        adults=6,
        children=0,
        addons=[
            AddOnSelection(
                label="Airport VIP meet", unit=AddOnUnit.PER_GROUP, unit_price_usd=Decimal("80")
            )
        ],
    )
    quote = calculate_quote(req, ALL_CLASSES)
    addon_line = next(li for li in quote["line_items"] if li["type"] == "ADDON")
    assert addon_line["subtotal"] == Decimal("80")


# ---------------------------------------------------------------------------
# Seasonal rates
# ---------------------------------------------------------------------------


def test_seasonal_multiplier_applied_when_start_date_in_range():
    multiplier = resolve_seasonal_multiplier(
        start_date=date(2026, 4, 15),
        date_from=date(2026, 4, 1),
        date_to=date(2026, 5, 31),
        multiplier=Decimal("1.20"),
    )
    assert multiplier == Decimal("1.20")


def test_seasonal_multiplier_not_applied_when_start_date_outside_range():
    multiplier = resolve_seasonal_multiplier(
        start_date=date(2026, 7, 1),
        date_from=date(2026, 4, 1),
        date_to=date(2026, 5, 31),
        multiplier=Decimal("1.20"),
    )
    assert multiplier == Decimal("1")


def test_seasonal_multiplier_flows_through_to_quote_total():
    req = QuoteRequest(
        start_date=date(2026, 4, 15),
        days=2,
        adults=2,
        children=0,
        seasonal_multiplier=Decimal("1.5"),
    )
    quote = calculate_quote(req, ALL_CLASSES)
    # subtotal: 2 days * $50 (sedan) = $100; total = $150 with 1.5x peak multiplier.
    assert quote["subtotal_usd"] == Decimal("100")
    assert quote["total_usd"] == Decimal("150.0")


# ---------------------------------------------------------------------------
# Child weighting
# ---------------------------------------------------------------------------


def test_child_weight_constant_is_one_half():
    assert CHILD_ENTRANCE_FARE_WEIGHT == Decimal("0.5")


def test_weighted_pax_halves_children_for_entrance_fees():
    assert weighted_pax(adults=2, children=2, entrance_fee=True) == Decimal("3")


def test_weighted_pax_full_price_when_not_entrance_fee():
    assert weighted_pax(adults=2, children=2, entrance_fee=False) == Decimal("4")


def test_per_person_entrance_activity_halves_child_fare_in_quote():
    req = QuoteRequest(
        start_date=date(2026, 5, 1),
        days=1,
        adults=2,
        children=2,
        activities=[
            ActivitySelection(
                label="Ark Fortress entrance",
                price_type=PriceType.PER_PERSON,
                unit_price_usd=Decimal("10"),
                is_entrance_fee=True,
            )
        ],
    )
    quote = calculate_quote(req, ALL_CLASSES)
    activity_line = next(li for li in quote["line_items"] if li["type"] == "ACTIVITY")
    # 2 full-price adults + 2 half-price children = 3 weighted pax * $10 = $30.
    assert activity_line["subtotal"] == Decimal("30")


# ---------------------------------------------------------------------------
# Structured breakdown shape / per-person display-only guarantee
# ---------------------------------------------------------------------------


def test_quote_breakdown_has_expected_shape():
    req = QuoteRequest(start_date=date(2026, 5, 1), days=2, adults=2, children=0)
    quote = calculate_quote(req, ALL_CLASSES)
    assert set(quote.keys()) == {
        "line_items",
        "vehicle_class",
        "vehicle_count",
        "subtotal_usd",
        "total_usd",
        "per_person_usd",
    }
    assert quote["total_usd"] == quote["subtotal_usd"]  # no seasonal multiplier -> unchanged


def test_per_person_usd_is_derived_display_value_not_primary_total():
    req = QuoteRequest(start_date=date(2026, 5, 1), days=2, adults=4, children=0)
    quote = calculate_quote(req, ALL_CLASSES)
    assert quote["per_person_usd"] == quote["total_usd"] / 4
    # The group total remains the primary figure.
    assert quote["total_usd"] != quote["per_person_usd"]


def test_select_vehicle_raises_on_empty_vehicle_classes():
    with pytest.raises(ValueError):
        select_vehicle([], adults=1, children=0)
