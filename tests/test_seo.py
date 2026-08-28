"""
SEO-layer smoke tests (CLAUDE.md §7): exactly one <h1> per page, sitemap.xml
and robots.txt actually work, and hreflang is gated on translation_complete
flags rather than being emitted unconditionally.
"""

import re

import pytest
from django.urls import reverse

from apps.catalog.models import Destination

pytestmark = pytest.mark.django_db

H1_RE = re.compile(rb"<h1[ >]")


@pytest.mark.parametrize(
    "url_name",
    ["core:home", "core:about", "core:faq", "core:contact", "core:reviews"],
)
def test_page_has_exactly_one_h1(client, url_name):
    response = client.get(reverse(url_name))
    assert response.status_code == 200
    assert len(H1_RE.findall(response.content)) == 1


def test_sitemap_xml_returns_200_and_valid_xml(client):
    response = client.get("/sitemap.xml")
    assert response.status_code == 200
    assert response["Content-Type"].startswith("application/xml")


def test_robots_txt_references_canonical_sitemap(client):
    response = client.get("/robots.txt")
    assert response.status_code == 200
    body = response.content.decode()
    assert "Sitemap:" in body
    assert "abdullohtours.com/sitemap.xml" in body
    assert "Disallow: /admin/" in body


def test_destination_detail_hreflang_omitted_for_incomplete_translation(client):
    destination = Destination.objects.create(
        slug="bukhara", name="Bukhara", is_active=True, translation_complete_ru=False
    )
    url = reverse("catalog:destination_detail", kwargs={"slug": destination.slug})
    response = client.get(url)
    body = response.content.decode()
    assert 'hreflang="en"' in body
    assert 'hreflang="x-default"' in body
    # RU translation is not marked complete -> must not be advertised to Google.
    assert 'hreflang="ru"' not in body


def test_destination_detail_hreflang_included_when_translation_complete(client):
    destination = Destination.objects.create(
        slug="khiva", name="Khiva", is_active=True, translation_complete_ru=True
    )
    url = reverse("catalog:destination_detail", kwargs={"slug": destination.slug})
    response = client.get(url)
    body = response.content.decode()
    assert 'hreflang="ru"' in body


def test_home_page_has_canonical_link(client):
    response = client.get(reverse("core:home"))
    body = response.content.decode()
    assert 'rel="canonical"' in body
