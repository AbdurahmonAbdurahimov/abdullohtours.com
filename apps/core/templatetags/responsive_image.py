"""Renders a full <img> tag with a WebP srcset for any WebPImageField value
(CLAUDE.md §7: responsive srcset, explicit width/height to avoid layout
shift, lazy-loading below the fold).

Variant filenames are derived purely from `apps.core.imaging` — no storage
existence check — so they stay in lockstep with what `WebPImageField.pre_save`
actually wrote at upload time. See apps/core/imaging.py's `variant_name`.
"""

from __future__ import annotations

from django import template
from django.forms.utils import flatatt
from django.utils.html import format_html

from apps.core.imaging import responsive_widths_for, variant_name

register = template.Library()


@register.simple_tag
def responsive_image(
    image_field,
    alt,
    width=None,
    height=None,
    css_class="",
    sizes="100vw",
    loading="lazy",
    fetchpriority=None,
):
    """
    {% responsive_image destination.hero_image destination.name width=destination.hero_image_width height=destination.hero_image_height css_class="w-full h-48 object-cover" sizes="(min-width: 768px) 50vw, 100vw" loading="lazy" %}

    `image_field` may be falsy (empty ImageField) — renders nothing so
    callers can drop the surrounding `{% if %}` they already have.

    Pass `loading="eager" fetchpriority="high"` for the one image expected
    to be the page's LCP element (e.g. the first card in a grid) — Lighthouse
    flags `loading="lazy"` on the LCP image as a performance regression
    since it delays the browser from discovering it (CLAUDE.md §7's
    Lighthouse ≥95 target).
    """
    if not image_field:
        return ""

    img_width = width or getattr(image_field, "width", None)
    img_height = height or getattr(image_field, "height", None)

    attrs = {
        "src": image_field.url,
        "alt": alt,
        "loading": loading,
        "decoding": "async",
    }
    if fetchpriority:
        attrs["fetchpriority"] = fetchpriority
    if css_class:
        attrs["class"] = css_class
    if img_width:
        attrs["width"] = img_width
    if img_height:
        attrs["height"] = img_height

    if img_width:
        candidates = [
            f"{image_field.storage.url(variant_name(image_field.name, w))} {w}w"
            for w in responsive_widths_for(img_width)
        ]
        candidates.append(f"{image_field.url} {img_width}w")
        attrs["srcset"] = ", ".join(candidates)
        attrs["sizes"] = sizes

    return format_html("<img{}>", flatatt(attrs))
