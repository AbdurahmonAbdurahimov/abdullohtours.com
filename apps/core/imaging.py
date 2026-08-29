"""
Image processing pipeline for uploaded ImageFields (CLAUDE.md §7): convert
every upload to WebP and generate a fixed set of smaller responsive-width
variants alongside it so templates can emit a `srcset`.

Runs synchronously inside `WebPImageField.pre_save` (see apps/core/fields.py)
— CLAUDE.md §2 rules out Celery/Redis, and Pillow is already a hard
dependency of Django's ImageField, so no new infrastructure is needed. A
single admin image upload is small enough that doing this inline, on the
request that saves the form, is not a meaningful latency concern.
"""

from __future__ import annotations

import io

from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from PIL import Image, ImageOps

WEBP_QUALITY = 82

# Ascending; only widths *smaller* than the original are ever generated —
# the original (converted) upload itself is always the largest candidate.
# Chosen against the design system's 1280px container (CLAUDE.md §3): 480
# covers a phone viewport, 768/1200 cover common tablet/desktop crops, 1920
# covers a full-bleed hero on a large screen.
RESPONSIVE_WIDTHS: tuple[int, ...] = (480, 768, 1200, 1920)


def convert_to_webp(file_obj, quality: int = WEBP_QUALITY) -> tuple[bytes, int, int]:
    """Re-encode an open image file as WebP. Returns (webp_bytes, width, height).

    Applies EXIF-based rotation first — phones/cameras store orientation as
    metadata rather than rotating pixels, and that metadata doesn't survive
    the re-encode, so skipping this would silently sideways/upside-down
    photos taken on a phone.
    """
    file_obj.seek(0)
    image = Image.open(file_obj)
    image = ImageOps.exif_transpose(image) or image

    if image.mode not in ("RGB", "RGBA"):
        has_alpha = image.mode in ("RGBA", "LA", "PA") or (
            image.mode == "P" and "transparency" in image.info
        )
        image = image.convert("RGBA" if has_alpha else "RGB")

    buffer = io.BytesIO()
    image.save(buffer, format="WEBP", quality=quality, method=6)
    return buffer.getvalue(), image.width, image.height


def resize_webp(webp_bytes: bytes, target_width: int, quality: int = WEBP_QUALITY) -> bytes:
    """Downscale an already-WebP image to `target_width`, preserving aspect ratio."""
    image = Image.open(io.BytesIO(webp_bytes))
    ratio = target_width / image.width
    target_height = max(1, round(image.height * ratio))
    resized = image.resize((target_width, target_height), Image.LANCZOS)
    buffer = io.BytesIO()
    resized.save(buffer, format="WEBP", quality=quality, method=6)
    return buffer.getvalue()


def variant_name(base_name: str, width: int) -> str:
    """`destinations/tashkent-hero.webp` -> `destinations/tashkent-hero-480w.webp`.

    Deterministic by construction: the template-side `responsive_image` tag
    (apps/core/templatetags/responsive_image.py) derives the same names from
    the same `RESPONSIVE_WIDTHS` without touching storage, so this naming
    scheme must stay in lockstep with that tag.
    """
    stem, _, ext = base_name.rpartition(".")
    return f"{stem}-{width}w.{ext}"


def responsive_widths_for(original_width: int) -> list[int]:
    """Widths (ascending) smaller than `original_width` — i.e. the variants
    actually worth generating/serving. Never upscale past the original.
    """
    return [w for w in RESPONSIVE_WIDTHS if w < original_width]


def generate_variants(
    storage: Storage, base_name: str, webp_bytes: bytes, original_width: int
) -> None:
    """Write each smaller responsive variant to `storage` next to `base_name`.

    Deletes-then-saves under the exact deterministic name rather than
    relying on `Storage.save()`'s default collision-renaming behaviour,
    since the template tag assumes these exact names exist without checking.
    """
    for width in responsive_widths_for(original_width):
        name = variant_name(base_name, width)
        if storage.exists(name):
            storage.delete(name)
        storage.save(name, ContentFile(resize_webp(webp_bytes, width)))
