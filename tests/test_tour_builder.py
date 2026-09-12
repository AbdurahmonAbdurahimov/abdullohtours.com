"""
Tests for the Tour Builder (CLAUDE.md §6): the multi-step Alpine.js/HTMX
flow at /build/, its server-rendered quote partial, BuilderSession
persistence, and the final submission into a BookingRequest.

Regression coverage: the builder was fully broken in production because
`x-data="tourBuilder({{ payload|safe }})"` embedded raw JSON (with its own
double quotes) into a double-quoted HTML attribute, truncating the Alpine
expression and leaving every field permanently hidden behind x-cloak. See
test_tour_builder_page_x_data_attribute_is_properly_escaped below.
"""

import re
from datetime import date
from decimal import Decimal

import pytest
from django.urls import reverse

from apps.bookings.models import BookingItem, BookingRequest, BuilderSession
from apps.catalog.models import AddOn, Car, Destination, VehicleClass

pytestmark = pytest.mark.django_db


def _make_catalog():
    destination = Destination.objects.create(slug="samarkand", name="Samarkand")
    vehicle_class = VehicleClass.objects.create(
        name="Sedan", min_pax=1, max_pax=3, daily_rate_usd=Decimal("50.00")
    )
    car = Car.objects.create(
        slug="sedan-1",
        name="Chevrolet Cobalt",
        vehicle_class=vehicle_class,
        capacity_pax=3,
    )
    addon = AddOn.objects.create(
        name="English-speaking guide",
        price_usd=Decimal("50.00"),
        unit=AddOn.Unit.PER_DAY,
    )
    return destination, vehicle_class, car, addon


def test_tour_builder_page_renders(client):
    _make_catalog()
    response = client.get(reverse("catalog:tour_builder"))
    assert response.status_code == 200


def test_tour_builder_page_x_data_attribute_is_properly_escaped(client):
    """Regression test for the "users can't use the builder" bug: the JSON
    blobs fed into x-data must be HTML-escaped (Django's default
    auto-escaping), not rendered with |safe, or their own double quotes
    break out of the x-data="..." attribute and Alpine never initializes.
    """
    _make_catalog()
    response = client.get(reverse("catalog:tour_builder"))
    html = response.content.decode()

    match = re.search(r'x-data="(tourBuilder\(.*?\))"', html)
    assert match, "expected a single x-data=\"tourBuilder(...)\" attribute"

    attr_value = match.group(1)
    # A real double quote here means the JSON leaked past the attribute
    # boundary instead of being escaped to &quot;.
    assert '"' not in attr_value, (
        "x-data attribute contains an unescaped double quote — this breaks "
        "the HTML attribute and Alpine's x-data expression entirely"
    )
    # The car -> vehicle class map should still be present, just escaped.
    assert "&quot;" in html


def test_build_quote_endpoint_returns_pricing_partial(client):
    destination, vehicle_class, car, addon = _make_catalog()
    response = client.post(
        reverse("catalog:build_quote"),
        data={
            "step": "1",
            "start_date": "2026-10-12",
            "end_date": "2026-10-19",
            "adults": "2",
            "children": "0",
        },
        HTTP_HX_REQUEST="true",
    )
    assert response.status_code == 200
    content = response.content.decode()
    assert "Estimated total" in content
    assert "$" in content


def test_build_quote_persists_builder_session(client):
    _make_catalog()
    session = client.session
    session.save()

    client.post(
        reverse("catalog:build_quote"),
        data={
            "step": "2",
            "start_date": "2026-10-12",
            "end_date": "2026-10-19",
            "adults": "3",
            "children": "1",
        },
    )

    builder_session = BuilderSession.objects.get(session_key=client.session.session_key)
    assert builder_session.last_step == 2
    assert builder_session.is_converted is False
    assert builder_session.payload["adults"] == 3


def test_build_submit_creates_booking_from_stored_session_not_client_totals(client):
    """The final total must come from the *stored* BuilderSession payload,
    recomputed server-side — never trusted from the browser."""
    destination, vehicle_class, car, addon = _make_catalog()

    client.post(
        reverse("catalog:build_quote"),
        data={
            "step": "1",
            "start_date": "2026-10-12",
            "end_date": "2026-10-14",
            "adults": "2",
            "children": "0",
            "destinations": [str(destination.id)],
            "addons": [str(addon.id)],
        },
    )

    response = client.post(
        reverse("catalog:build_submit"),
        data={
            "full_name": "Elena Rostova",
            "email": "elena@example.com",
            "phone": "+44 7700 900077",
            "whatsapp": "",
            "country": "UK",
            "message": "",
            "website": "",
        },
    )

    assert response.status_code == 302
    booking = BookingRequest.objects.get(email="elena@example.com")
    assert booking.source_type == BookingRequest.SourceType.BUILDER
    assert booking.vehicle_class_id == vehicle_class.id
    # 3 days transport (50*3) + 3 days guide add-on (50*3) = 300
    assert booking.estimated_total_usd == Decimal("300.00")
    assert BookingItem.objects.filter(request=booking).exists()

    builder_session = BuilderSession.objects.get(session_key=client.session.session_key)
    assert builder_session.is_converted is True


def test_build_submit_without_builder_session_redirects_to_builder(client):
    response = client.post(
        reverse("catalog:build_submit"),
        data={
            "full_name": "Elena Rostova",
            "email": "elena@example.com",
            "phone": "",
            "whatsapp": "",
            "country": "UK",
            "message": "",
            "website": "",
        },
    )
    assert response.status_code == 302
    assert response.url == reverse("catalog:tour_builder")
    assert not BookingRequest.objects.exists()


def test_build_submit_rejects_honeypot(client):
    _make_catalog()
    client.post(
        reverse("catalog:build_quote"),
        data={"step": "1", "adults": "1", "children": "0"},
    )
    response = client.post(
        reverse("catalog:build_submit"),
        data={
            "full_name": "Bot",
            "email": "bot@example.com",
            "phone": "",
            "whatsapp": "",
            "country": "",
            "message": "",
            "website": "http://spam.example",
        },
    )
    assert response.status_code == 200
    assert not BookingRequest.objects.filter(email="bot@example.com").exists()


def test_quote_without_seeded_vehicle_classes_does_not_crash(client):
    """Empty catalog (fresh install, no seed data yet) must render a
    placeholder quote instead of calculate_quote() raising."""
    response = client.get(reverse("catalog:tour_builder"))
    assert response.status_code == 200
    assert "$0.00" in response.content.decode()
