"""Custom ImageField that transparently applies the WebP conversion +
responsive-variant pipeline from apps.core.imaging to every new upload
(CLAUDE.md §7). Swap `models.ImageField` for `WebPImageField` — the admin
widget, `.url`, and `width_field`/`height_field` behaviour are unchanged;
`width_field`/`height_field` end up populated from the *converted* WebP's
dimensions, which is what templates use for the CLS-preventing explicit
width/height (see apps/core/templatetags/responsive_image.py).
"""

from __future__ import annotations

from django.core.files.base import ContentFile
from django.db import models

from . import imaging


class WebPImageField(models.ImageField):
    def pre_save(self, model_instance, add):
        file = getattr(model_instance, self.attname)

        webp_bytes = width = None
        if file and not file._committed:
            # A genuinely new upload (not a previously-saved WebP being
            # re-saved untouched) — convert before Django commits it to
            # storage, so what actually lands on disk is already WebP.
            webp_bytes, width, _height = imaging.convert_to_webp(file.file)
            stem = file.name.rsplit(".", 1)[0]
            file.name = f"{stem}.webp"
            file.file = ContentFile(webp_bytes, name=file.name)

        file = super().pre_save(model_instance, add)

        if webp_bytes is not None and file:
            # `file.name` is now the final, storage-committed name (Django
            # may have de-duplicated it) — derive variant filenames from
            # that, not the pre-commit name, so they actually sit next to it.
            imaging.generate_variants(file.storage, file.name, webp_bytes, width)

        return file
