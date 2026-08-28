"""
Pure pricing engine for Abdulloh Tours (CLAUDE.md §5).

Deliberately decoupled from the ORM: every function here takes plain
dataclasses/values and returns plain dicts, so the whole module is fast to
unit test (see tests/test_pricing.py) and safe to call from a view that
builds its inputs from request.POST + a handful of DB lookups. All pricing
is computed server-side — the Alpine.js tour builder POSTs a selection to
/api/quote/ and renders whatever calculate_quote() returns; nothing is ever
computed in JavaScript.

Display rule (CLAUDE.md §5 + the "avoid per-person pricing" defect called
out in §3's mockup review): the primary number is always `total_usd` /
`subtotal_usd` — the per-vehicle group total. `per_person_usd` on the
returned breakdown is informational only, to help a family understand their
share; nothing in this module treats it as the real price, and templates
must show "Estimated total" (never "final price") next to the group total,
not the per-person figure.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from enum import StrEnum

# Children under 12 count as this weight for PER_PERSON, entrance-fee-style
# pricing (Activity.PER_PERSON, and per-person AddOns that are inherently
# per-head like entrance tickets). They still count as FULL weight (1.0) for
# vehicle capacity / vehicle-class selection — a child still occupies a seat.
CHILD_ENTRANCE_FARE_WEIGHT = Decimal("0.5")


class PriceType(StrEnum):
    PER_VEHICLE = "PER_VEHICLE"
    PER_PERSON = "PER_PERSON"
    PER_DAY = "PER_DAY"


class AddOnUnit(StrEnum):
    PER_PERSON = "PER_PERSON"
    PER_DAY = "PER_DAY"
    PER_GROUP = "PER_GROUP"
    PER_NIGHT = "PER_NIGHT"


# ---------------------------------------------------------------------------
# Plain input shapes
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class VehicleClassOption:
    """Snapshot of a catalog.VehicleClass row, decoupled from the DB."""

    id: int
    name: str
    max_pax: int
    daily_rate_usd: Decimal


@dataclass(frozen=True)
class ActivitySelection:
    label: str
    price_type: PriceType
    unit_price_usd: Decimal
    # PER_PERSON activities are typically entrance-fee-like (child discount
    # applies). Set False for a PER_PERSON activity that should charge full
    # price per head regardless of age (rare, but the flag keeps the rule
    # explicit rather than hardcoded).
    is_entrance_fee: bool = True


@dataclass(frozen=True)
class AddOnSelection:
    label: str
    unit: AddOnUnit
    unit_price_usd: Decimal


@dataclass(frozen=True)
class QuoteRequest:
    start_date: date
    days: int
    adults: int
    children: int = 0
    manual_vehicle_class_id: int | None = None
    activities: list[ActivitySelection] = field(default_factory=list)
    addons: list[AddOnSelection] = field(default_factory=list)
    # Nights for PER_NIGHT addons (hotel). Defaults to days - 1 (a standard
    # N-day / N-1-night trip) when not given explicitly.
    nights: int | None = None
    # Resolved via resolve_seasonal_multiplier() before building the
    # request — see that function's docstring for why this is a single
    # global multiplier rather than per-line-item.
    seasonal_multiplier: Decimal = Decimal("1")

    @property
    def resolved_nights(self) -> int:
        return self.nights if self.nights is not None else max(self.days - 1, 0)


# ---------------------------------------------------------------------------
# Vehicle selection
# ---------------------------------------------------------------------------


def select_vehicle(
    vehicle_classes: list[VehicleClassOption],
    adults: int,
    children: int,
    manual_vehicle_class_id: int | None = None,
) -> tuple[VehicleClassOption, int]:
    """Pick a vehicle class + vehicle count for a given party size.

    - Children count FULL weight for capacity (a child still needs a seat).
    - Auto-selection picks the smallest class that fits the whole party in
      a single vehicle; if the party is bigger than the largest available
      class, it falls back to the largest class and overflows into multiple
      vehicles of that class.
    - A manual override is only honored if it is an upgrade (same class or
      larger) relative to the auto-selected class — a downgrade that would
      not fit the party is silently ignored and the auto-selected class is
      used instead.
    """
    if not vehicle_classes:
        raise ValueError("No vehicle classes available to select from.")

    total_pax = adults + children

    # Order classes by capacity (tie-broken by price) to get a stable notion
    # of "upgrade" even when two classes share the same max_pax.
    sorted_classes = sorted(vehicle_classes, key=lambda vc: (vc.max_pax, vc.daily_rate_usd))

    required_idx = next(
        (i for i, vc in enumerate(sorted_classes) if vc.max_pax >= total_pax),
        len(sorted_classes) - 1,  # nothing fits alone -> largest class, overflow to N vehicles
    )
    required = sorted_classes[required_idx]
    chosen = required

    if manual_vehicle_class_id is not None:
        manual_idx = next(
            (i for i, vc in enumerate(sorted_classes) if vc.id == manual_vehicle_class_id),
            None,
        )
        if manual_idx is not None and manual_idx >= required_idx:
            chosen = sorted_classes[manual_idx]
        # else: downgrade attempt (or unknown id) -> ignored, keep `required`.

    vehicle_count = max(1, math.ceil(total_pax / chosen.max_pax)) if total_pax else 1

    return chosen, vehicle_count


# ---------------------------------------------------------------------------
# Seasonal rates
# ---------------------------------------------------------------------------


def resolve_seasonal_multiplier(
    start_date: date, date_from: date, date_to: date, multiplier: Decimal
) -> Decimal:
    """Return `multiplier` if start_date falls within [date_from, date_to], else 1.

    catalog.SeasonalRate rows with `activity=None` apply globally to a whole
    quote; the view layer picks the applicable SeasonalRate row(s) for the
    trip's start_date and folds the result into QuoteRequest.seasonal_multiplier
    before calling calculate_quote(). Keeping this as a single resolved
    multiplier (rather than a per-line-item lookup baked into this module)
    keeps calculate_quote() free of any DB/date-range concerns.
    """
    if date_from <= start_date <= date_to:
        return multiplier
    return Decimal("1")


# ---------------------------------------------------------------------------
# Weighted pax helper
# ---------------------------------------------------------------------------


def weighted_pax(adults: int, children: int, entrance_fee: bool = True) -> Decimal:
    """Party size for PER_PERSON pricing.

    Entrance-fee-style items (the default): children count at
    CHILD_ENTRANCE_FARE_WEIGHT. Non-entrance-fee PER_PERSON items charge
    full price per head regardless of age.
    """
    if entrance_fee:
        return Decimal(adults) + Decimal(children) * CHILD_ENTRANCE_FARE_WEIGHT
    return Decimal(adults + children)


# ---------------------------------------------------------------------------
# Quote calculation
# ---------------------------------------------------------------------------


def calculate_quote(request: QuoteRequest, vehicle_classes: list[VehicleClassOption]) -> dict:
    """Compute a full structured price breakdown for a trip selection."""
    vehicle_class, vehicle_count = select_vehicle(
        vehicle_classes, request.adults, request.children, request.manual_vehicle_class_id
    )

    full_pax = Decimal(request.adults + request.children)
    line_items: list[dict] = []

    # 1. Transport — always the first line item.
    transport_qty = Decimal(request.days) * vehicle_count
    transport_subtotal = vehicle_class.daily_rate_usd * transport_qty
    line_items.append(
        {
            "label": f"Transport — {vehicle_class.name}"
            + (f" x{vehicle_count}" if vehicle_count > 1 else ""),
            "unit_price": vehicle_class.daily_rate_usd,
            "qty": transport_qty,
            "subtotal": transport_subtotal,
            "type": "TRANSPORT",
        }
    )

    # 2. Activities.
    for act in request.activities:
        if act.price_type == PriceType.PER_VEHICLE:
            qty = Decimal(vehicle_count)
        elif act.price_type == PriceType.PER_PERSON:
            qty = weighted_pax(request.adults, request.children, act.is_entrance_fee)
        elif act.price_type == PriceType.PER_DAY:
            qty = Decimal(request.days)
        else:  # pragma: no cover - guarded by PriceType enum
            raise ValueError(f"Unknown activity price_type: {act.price_type!r}")

        subtotal = act.unit_price_usd * qty
        line_items.append(
            {
                "label": act.label,
                "unit_price": act.unit_price_usd,
                "qty": qty,
                "subtotal": subtotal,
                "type": "ACTIVITY",
            }
        )

    # 3. Add-ons.
    nights = Decimal(request.resolved_nights)
    for addon in request.addons:
        if addon.unit == AddOnUnit.PER_PERSON:
            qty = full_pax
        elif addon.unit == AddOnUnit.PER_DAY:
            qty = Decimal(request.days)
        elif addon.unit == AddOnUnit.PER_GROUP:
            qty = Decimal(1)
        elif addon.unit == AddOnUnit.PER_NIGHT:
            qty = full_pax * nights
        else:  # pragma: no cover - guarded by AddOnUnit enum
            raise ValueError(f"Unknown addon unit: {addon.unit!r}")

        subtotal = addon.unit_price_usd * qty
        line_items.append(
            {
                "label": addon.label,
                "unit_price": addon.unit_price_usd,
                "qty": qty,
                "subtotal": subtotal,
                "type": "ADDON",
            }
        )

    subtotal_usd = sum((li["subtotal"] for li in line_items), Decimal("0"))
    total_usd = subtotal_usd * request.seasonal_multiplier
    per_person_usd = (total_usd / full_pax) if full_pax else Decimal("0")

    return {
        "line_items": line_items,
        "vehicle_class": vehicle_class,
        "vehicle_count": vehicle_count,
        "subtotal_usd": subtotal_usd,
        "total_usd": total_usd,
        "per_person_usd": per_person_usd,
    }
