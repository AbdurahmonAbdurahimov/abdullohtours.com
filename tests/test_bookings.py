"""
Tests for apps.bookings: ref_code generation, the honeypot spam guard, the
booking-request request/thanks flow, frozen BookingItem price snapshots, and
the soft availability logic (CLAUDE.md §10).
"""

import re
from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.urls import reverse

from apps.bookings.availability import is_limited_availability
from apps.bookings.forms import BookingRequestForm
from apps.bookings.models import BookingItem, BookingRequest
from apps.catalog.models import Activity, Destination, Vehicle, VehicleClass

pytestmark = pytest.mark.django_db


REF_CODE_RE = re.compile(r"^AB-\d{4}$")


def _make_booking_request(**overrides) -> BookingRequest:
    defaults = dict(
        source_type=BookingRequest.SourceType.DIRECT,
        full_name="Elena Rostova",
        email="elena@example.com",
        phone="+44 7700 900077",
        country="UK",
    )
    defaults.update(overrides)
    return BookingRequest.objects.create(**defaults)


def test_ref_code_is_auto_generated_in_expected_format():
    booking = _make_booking_request()
    assert REF_CODE_RE.match(booking.ref_code)


def test_ref_code_is_not_overwritten_on_resave():
    booking = _make_booking_request()
    original = booking.ref_code
    booking.status = BookingRequest.Status.CONTACTED
    booking.save()
    booking.refresh_from_db()
    assert booking.ref_code == original


def test_honeypot_field_rejects_submission():
    form = BookingRequestForm(
        data={
            "full_name": "Bot",
            "email": "bot@example.com",
            "phone": "",
            "whatsapp": "",
            "country": "",
            "message": "",
            "website": "http://spam.example",  # filled -> bot
        }
    )
    assert not form.is_valid()
    assert "website" in form.errors


def test_valid_form_without_honeypot_is_accepted():
    form = BookingRequestForm(
        data={
            "full_name": "Real Tourist",
            "email": "tourist@example.com",
            "phone": "+1 555 0100",
            "whatsapp": "",
            "country": "US",
            "message": "Interested in a Samarkand trip.",
            "website": "",
        }
    )
    assert form.is_valid(), form.errors


def test_booking_request_view_creates_request_and_redirects_to_thanks(client):
    url = reverse("bookings:booking_request")
    response = client.post(
        url,
        data={
            "full_name": "Real Tourist",
            "email": "tourist@example.com",
            "phone": "+1 555 0100",
            "whatsapp": "",
            "country": "US",
            "message": "",
            "website": "",
        },
    )
    assert response.status_code == 302
    booking = BookingRequest.objects.get(email="tourist@example.com")
    assert booking.source_type == BookingRequest.SourceType.DIRECT
    assert (
        response.url.endswith(f"/request/{booking.ref_code}/thanks/")
        or f"/{booking.ref_code}/" in response.url
    )


def test_thanks_page_renders_ref_code(client):
    booking = _make_booking_request()
    url = reverse("bookings:thanks", kwargs={"ref_code": booking.ref_code})
    response = client.get(url)
    assert response.status_code == 200
    assert booking.ref_code in response.content.decode()


def test_booking_item_price_is_frozen_when_activity_price_changes():
    destination = Destination.objects.create(slug="samarkand", name="Samarkand")
    activity = Activity.objects.create(
        destination=destination,
        title="Registan entrance",
        slug="registan-entrance",
        price_type=Activity.PriceType.PER_PERSON,
        base_price_usd=Decimal("10.00"),
    )
    booking = _make_booking_request()
    item = BookingItem.objects.create(
        request=booking,
        item_type=BookingItem.ItemType.ACTIVITY,
        label=activity.title,
        unit_price_usd=activity.base_price_usd,
        quantity=2,
        subtotal_usd=activity.base_price_usd * 2,
    )

    # Admin changes the live catalog price tomorrow...
    activity.base_price_usd = Decimal("25.00")
    activity.save()

    item.refresh_from_db()
    # ...but the frozen snapshot on the existing request must not change.
    assert item.unit_price_usd == Decimal("10.00")
    assert item.subtotal_usd == Decimal("20.00")


def test_availability_not_limited_with_no_confirmed_requests():
    Vehicle.objects.create(
        name="Sedan #1",
        vehicle_class=VehicleClass.objects.create(
            name="Sedan", min_pax=1, max_pax=3, daily_rate_usd=50
        ),
        is_active=True,
    )
    assert is_limited_availability(date(2026, 6, 1)) is False


def test_availability_limited_when_confirmed_requests_meet_fleet_size():
    vehicle_class = VehicleClass.objects.create(
        name="Sedan", min_pax=1, max_pax=3, daily_rate_usd=50
    )
    Vehicle.objects.create(name="Sedan #1", vehicle_class=vehicle_class, is_active=True)

    check_date = date(2026, 6, 1)
    _make_booking_request(
        email="a@example.com",
        status=BookingRequest.Status.CONFIRMED,
        start_date=check_date - timedelta(days=1),
        end_date=check_date + timedelta(days=1),
    )

    assert is_limited_availability(check_date) is True
