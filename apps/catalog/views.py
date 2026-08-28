import json
from datetime import date
from decimal import Decimal

from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit

from apps.bookings.availability import availability_summary
from apps.bookings.forms import BookingRequestForm
from apps.bookings.models import BookingItem, BookingRequest, BuilderSession

from . import pricing
from .models import (
    Activity,
    AddOn,
    Destination,
    Package,
    RoutePage,
    SeasonalRate,
    VehicleClass,
)


def destination_index(request: HttpRequest) -> HttpResponse:
    destinations = Destination.objects.filter(is_active=True)
    return render(request, "catalog/destination_index.html", {"destinations": destinations})


def destination_detail(request: HttpRequest, slug: str) -> HttpResponse:
    destination = get_object_or_404(Destination, slug=slug, is_active=True)
    return render(request, "catalog/destination_detail.html", {"destination": destination})


def package_index(request: HttpRequest) -> HttpResponse:
    packages = Package.objects.filter(is_active=True)
    return render(request, "catalog/package_index.html", {"packages": packages})


def package_detail(request: HttpRequest, slug: str) -> HttpResponse:
    package = get_object_or_404(Package, slug=slug, is_active=True)
    return render(request, "catalog/package_detail.html", {"package": package})


def route_index(request: HttpRequest) -> HttpResponse:
    """Programmatic SEO landing pages (CLAUDE.md §13 Phase 3) — one per
    destination pair, e.g. "Samarkand & Bukhara Tour"."""
    routes = RoutePage.objects.filter(is_active=True).select_related(
        "destination_a", "destination_b"
    )
    return render(request, "catalog/route_index.html", {"routes": routes})


def route_detail(request: HttpRequest, slug: str) -> HttpResponse:
    route = get_object_or_404(
        RoutePage.objects.select_related("destination_a", "destination_b"),
        slug=slug,
        is_active=True,
    )
    return render(request, "catalog/route_detail.html", {"route": route})


def tour_builder(
    request: HttpRequest,
    *,
    initial_step: int = 1,
    contact_form=None,
    builder_payload: dict | None = None,
) -> HttpResponse:
    """The 5-step Tour Builder (CLAUDE.md §6): dates+travellers, destinations,
    activities, add-ons, contact. Vehicle class is derived automatically from
    party size (apps.catalog.pricing.select_vehicle) and shown read-only in
    the sticky summary — never a separate step, never a free pick below the
    party's required capacity.

    All pricing shown to the visitor comes from the /build/quote/ HTMX
    endpoint below, which calls apps.catalog.pricing.calculate_quote()
    server-side — this view only supplies the catalog options to choose from.
    """
    if not request.session.session_key:
        request.session.create()

    destinations = Destination.objects.filter(is_active=True)
    activities = Activity.objects.filter(
        is_active=True, destination__is_active=True
    ).select_related("destination")
    addons = AddOn.objects.filter(is_active=True)
    vehicle_classes = VehicleClass.objects.all()
    payload = builder_payload or {}
    if not payload and request.GET.getlist("destination"):
        # "Build a private tour" CTA from a destination or route landing page
        # — preselect one or more destinations (?destination=1&destination=2).
        payload = {"destinations": request.GET.getlist("destination")}

    return render(
        request,
        "catalog/tour_builder.html",
        {
            "destinations": destinations,
            "activities": activities,
            "addons": addons,
            "vehicle_classes": vehicle_classes,
            "initial_step": initial_step,
            "contact_form": contact_form or BookingRequestForm(),
            "quote": _quote_from_payload(payload),
            "builder_payload_json": json.dumps(payload),
        },
    )


def _parse_date(raw: str | None) -> date | None:
    if not raw:
        return None
    try:
        return date.fromisoformat(raw)
    except ValueError:
        return None


def _build_quote_request(
    *,
    start_date: date | None,
    end_date: date | None,
    adults: int,
    children: int,
    activity_ids: list[str],
    addon_ids: list[str],
    manual_vehicle_class_id: int | None,
) -> tuple[pricing.QuoteRequest, list[pricing.VehicleClassOption]]:
    """Shared construction used by both build_quote() (live pricing while the
    visitor is still choosing) and build_submit() (the authoritative,
    server-recomputed total at the moment of booking).
    """
    days = max((end_date - start_date).days + 1, 1) if start_date and end_date else 1

    vehicle_classes = [
        pricing.VehicleClassOption(
            id=vc.id, name=vc.name, max_pax=vc.max_pax, daily_rate_usd=vc.daily_rate_usd
        )
        for vc in VehicleClass.objects.all()
    ]

    activity_selections = [
        pricing.ActivitySelection(
            label=a.title,
            price_type=pricing.PriceType(a.price_type),
            unit_price_usd=a.base_price_usd,
        )
        for a in Activity.objects.filter(id__in=activity_ids, is_active=True)
    ]

    addon_selections = [
        pricing.AddOnSelection(
            label=a.name,
            unit=pricing.AddOnUnit(a.unit),
            unit_price_usd=a.price_usd,
        )
        for a in AddOn.objects.filter(id__in=addon_ids, is_active=True)
    ]

    # Global SeasonalRate rows only (activity=None) — calculate_quote() takes
    # a single resolved multiplier for the whole quote, per pricing.py's
    # resolve_seasonal_multiplier() docstring.
    seasonal_multiplier = Decimal("1")
    if start_date:
        for rate in SeasonalRate.objects.filter(activity__isnull=True):
            seasonal_multiplier = max(
                seasonal_multiplier,
                pricing.resolve_seasonal_multiplier(
                    start_date, rate.date_from, rate.date_to, rate.multiplier
                ),
            )

    quote_request = pricing.QuoteRequest(
        start_date=start_date or date.today(),
        days=days,
        adults=adults,
        children=children,
        manual_vehicle_class_id=manual_vehicle_class_id,
        activities=activity_selections,
        addons=addon_selections,
        nights=max(days - 1, 0),
        seasonal_multiplier=seasonal_multiplier,
    )
    return quote_request, vehicle_classes


def _selection_from_post(data) -> dict:
    start_date = _parse_date(data.get("start_date"))
    end_date = _parse_date(data.get("end_date"))
    try:
        adults = max(int(data.get("adults") or 1), 1)
    except ValueError:
        adults = 1
    try:
        children = max(int(data.get("children") or 0), 0)
    except ValueError:
        children = 0
    manual_vehicle_class_id = data.get("vehicle_class") or None
    return {
        "start_date": start_date.isoformat() if start_date else None,
        "end_date": end_date.isoformat() if end_date else None,
        "adults": adults,
        "children": children,
        "destinations": data.getlist("destinations"),
        "activities": data.getlist("activities"),
        "addons": data.getlist("addons"),
        "manual_vehicle_class_id": manual_vehicle_class_id,
    }


def _quote_from_payload(payload: dict) -> dict:
    start_date = _parse_date(payload.get("start_date"))
    end_date = _parse_date(payload.get("end_date"))

    if not VehicleClass.objects.exists():
        # Catalog isn't seeded yet (seed data is a separate follow-up task) —
        # render a placeholder quote instead of calculate_quote() raising on
        # an empty vehicle_classes list.
        return {
            "line_items": [],
            "vehicle_class": None,
            "vehicle_count": 0,
            "subtotal_usd": Decimal("0"),
            "total_usd": Decimal("0"),
            "per_person_usd": Decimal("0"),
            "start_date": start_date,
            "end_date": end_date,
            "adults": payload.get("adults", 1),
            "children": payload.get("children", 0),
            "destinations": Destination.objects.none(),
            "availability": None,
        }

    manual_vehicle_class_id = payload.get("manual_vehicle_class_id")
    quote_request, vehicle_classes = _build_quote_request(
        start_date=start_date,
        end_date=end_date,
        adults=payload.get("adults", 1),
        children=payload.get("children", 0),
        activity_ids=payload.get("activities", []),
        addon_ids=payload.get("addons", []),
        manual_vehicle_class_id=int(manual_vehicle_class_id) if manual_vehicle_class_id else None,
    )
    breakdown = pricing.calculate_quote(quote_request, vehicle_classes)
    breakdown["start_date"] = start_date
    breakdown["end_date"] = end_date
    breakdown["adults"] = quote_request.adults
    breakdown["children"] = quote_request.children
    breakdown["destinations"] = Destination.objects.filter(id__in=payload.get("destinations", []))
    breakdown["availability"] = availability_summary(start_date) if start_date else None
    return breakdown


def _save_builder_session(
    request: HttpRequest, payload: dict, step: int, total_usd: Decimal
) -> None:
    session_obj = (
        BuilderSession.objects.filter(session_key=request.session.session_key, is_converted=False)
        .order_by("-created_at")
        .first()
    ) or BuilderSession(session_key=request.session.session_key)
    session_obj.payload = payload
    session_obj.last_step = step
    session_obj.estimated_total_usd = total_usd
    session_obj.save()


@require_POST
def build_quote(request: HttpRequest) -> HttpResponse:
    """HTMX endpoint the builder POSTs the current selection to on every
    change. Computes the quote server-side (CLAUDE.md §5 — never in JS),
    persists a BuilderSession row so abandoned builders are visible in the
    admin (CLAUDE.md §6), and returns the summary partial to swap in.
    """
    if not request.session.session_key:
        request.session.create()

    payload = _selection_from_post(request.POST)
    breakdown = _quote_from_payload(payload)

    try:
        step = int(request.POST.get("step") or 1)
    except ValueError:
        step = 1
    _save_builder_session(request, payload, step, breakdown["total_usd"])

    return render(request, "catalog/partials/quote_summary.html", {"quote": breakdown})


@ratelimit(key="ip", rate="5/h", method="POST", block=True)
def build_submit(request: HttpRequest) -> HttpResponse:
    """Step 5 submission: create the BookingRequest from the *stored*
    BuilderSession payload, never from client-submitted totals — the price
    is recomputed here from scratch via apps.catalog.pricing so nothing the
    browser sent is trusted as the final number.
    """
    if request.method != "POST":
        return redirect("catalog:tour_builder")

    session_obj = (
        BuilderSession.objects.filter(session_key=request.session.session_key, is_converted=False)
        .order_by("-created_at")
        .first()
    )
    if session_obj is None:
        return redirect("catalog:tour_builder")

    form = BookingRequestForm(request.POST)
    if not form.is_valid():
        return tour_builder(
            request, initial_step=5, contact_form=form, builder_payload=session_obj.payload
        )

    breakdown = _quote_from_payload(session_obj.payload)

    booking: BookingRequest = form.save(commit=False)
    booking.source_type = BookingRequest.SourceType.BUILDER
    booking.custom_payload = session_obj.payload
    booking.start_date = breakdown["start_date"]
    booking.end_date = breakdown["end_date"]
    booking.adults = breakdown["adults"]
    booking.children = breakdown["children"]
    booking.vehicle_class = (
        VehicleClass.objects.filter(pk=breakdown["vehicle_class"].id).first()
        if breakdown["vehicle_class"]
        else None
    )
    booking.estimated_total_usd = breakdown["total_usd"]
    booking.save()

    for item in breakdown["line_items"]:
        BookingItem.objects.create(
            request=booking,
            item_type=item["type"],
            label=item["label"],
            unit_price_usd=item["unit_price"],
            quantity=item["qty"],
            subtotal_usd=item["subtotal"],
        )

    session_obj.is_converted = True
    session_obj.save(update_fields=["is_converted"])

    return redirect(reverse("bookings:thanks", kwargs={"ref_code": booking.ref_code}))
