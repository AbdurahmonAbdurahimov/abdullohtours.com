"""
Tests for the WebP conversion / responsive-srcset image pipeline
(CLAUDE.md §7): apps/core/imaging.py, apps/core/fields.py's WebPImageField,
and the `responsive_image` template tag.
"""

import io

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.template import Context, Template
from PIL import Image

from apps.catalog.models import Destination
from apps.core.imaging import (
    RESPONSIVE_WIDTHS,
    convert_to_webp,
    responsive_widths_for,
    variant_name,
)

pytestmark = pytest.mark.django_db


def _jpeg_bytes(width: int, height: int, color=(200, 30, 30)) -> io.BytesIO:
    buf = io.BytesIO()
    Image.new("RGB", (width, height), color=color).save(buf, format="JPEG")
    buf.seek(0)
    return buf


def test_convert_to_webp_produces_valid_webp_and_preserves_dimensions():
    source = _jpeg_bytes(600, 300)
    webp_bytes, width, height = convert_to_webp(source)

    assert width == 600
    assert height == 300
    reopened = Image.open(io.BytesIO(webp_bytes))
    assert reopened.format == "WEBP"
    assert reopened.size == (600, 300)


def test_convert_to_webp_flattens_transparency_correctly():
    buf = io.BytesIO()
    Image.new("RGBA", (100, 50), color=(0, 0, 0, 0)).save(buf, format="PNG")
    buf.seek(0)

    webp_bytes, width, height = convert_to_webp(buf)

    reopened = Image.open(io.BytesIO(webp_bytes))
    assert reopened.mode == "RGBA"
    assert (width, height) == (100, 50)


def test_responsive_widths_for_never_upscales():
    assert responsive_widths_for(2000) == list(RESPONSIVE_WIDTHS)
    assert responsive_widths_for(600) == [w for w in RESPONSIVE_WIDTHS if w < 600]
    assert responsive_widths_for(100) == []


def test_variant_name_inserts_width_before_extension():
    assert variant_name("destinations/tashkent-hero.webp", 480) == (
        "destinations/tashkent-hero-480w.webp"
    )


def test_webp_image_field_converts_upload_and_generates_variants():
    destination = Destination.objects.create(slug="test-dest", name="Test", is_active=True)

    upload = SimpleUploadedFile(
        "photo.jpg", _jpeg_bytes(2000, 1000).read(), content_type="image/jpeg"
    )
    destination.hero_image = upload
    destination.save()
    destination.refresh_from_db()

    assert destination.hero_image.name.endswith(".webp")
    assert destination.hero_image_width == 2000
    assert destination.hero_image_height == 1000

    storage = destination.hero_image.storage
    assert storage.exists(destination.hero_image.name)
    for width in responsive_widths_for(2000):
        assert storage.exists(variant_name(destination.hero_image.name, width))

    # Cleanup: delete the original and every variant this test wrote.
    storage.delete(destination.hero_image.name)
    for width in responsive_widths_for(2000):
        storage.delete(variant_name(destination.hero_image.name, width))


def test_webp_image_field_does_not_reprocess_on_unrelated_resave():
    destination = Destination.objects.create(slug="test-dest-2", name="Test 2", is_active=True)
    upload = SimpleUploadedFile(
        "photo2.jpg", _jpeg_bytes(900, 600).read(), content_type="image/jpeg"
    )
    destination.hero_image = upload
    destination.save()
    destination.refresh_from_db()
    stored_name = destination.hero_image.name

    # Resaving without touching the image must not rename/reconvert it.
    destination.name = "Test 2 renamed"
    destination.save()
    destination.refresh_from_db()

    assert destination.hero_image.name == stored_name

    storage = destination.hero_image.storage
    storage.delete(stored_name)
    for width in responsive_widths_for(900):
        storage.delete(variant_name(stored_name, width))


def test_responsive_image_tag_renders_srcset_and_dimensions():
    destination = Destination.objects.create(slug="test-dest-3", name="Test 3", is_active=True)
    upload = SimpleUploadedFile(
        "photo3.jpg", _jpeg_bytes(1200, 600).read(), content_type="image/jpeg"
    )
    destination.hero_image = upload
    destination.save()
    destination.refresh_from_db()

    template = Template(
        "{% load responsive_image %}"
        "{% responsive_image d.hero_image d.name width=d.hero_image_width "
        'height=d.hero_image_height loading="eager" %}'
    )
    html = template.render(Context({"d": destination}))

    assert 'width="1200"' in html
    assert 'height="600"' in html
    assert 'loading="eager"' in html
    assert "srcset=" in html
    assert "480w" in html and "768w" in html
    assert "1920w" not in html  # never upscale past the 1200px original

    storage = destination.hero_image.storage
    storage.delete(destination.hero_image.name)
    for width in responsive_widths_for(1200):
        storage.delete(variant_name(destination.hero_image.name, width))


def test_responsive_image_tag_renders_nothing_for_empty_field():
    destination = Destination.objects.create(slug="test-dest-4", name="Test 4", is_active=True)
    template = Template("{% load responsive_image %}{% responsive_image d.hero_image d.name %}")
    html = template.render(Context({"d": destination}))
    assert html == ""
