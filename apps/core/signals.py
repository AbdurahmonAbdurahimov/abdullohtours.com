"""Deletes a WebPImageField's file (+ responsive variants) from storage when
the row that owns it is deleted. Django never does this on its own for a
plain FileField/ImageField — the replace/clear case is instead handled in
WebPImageField.pre_save (apps/core/fields.py); this covers the third way a
file becomes orphaned.

Connected generically (no `sender=`) in CoreConfig.ready() so every model
with a WebPImageField is covered without per-model boilerplate — the
receiver itself is a no-op for any model that doesn't have one.
"""

from __future__ import annotations

from . import imaging
from .fields import WebPImageField


def cleanup_webp_images_on_delete(sender, instance, **kwargs):
    for field in sender._meta.get_fields():
        if not isinstance(field, WebPImageField):
            continue
        file = getattr(instance, field.attname, None)
        if not file:
            continue
        width = getattr(instance, field.width_field, None) if field.width_field else None
        imaging.delete_with_variants(file.storage, file.name, width)
