"""Custom ImageField that transparently applies the WebP conversion +
responsive-variant pipeline from apps.core.imaging to every new upload
(CLAUDE.md §7). Swap `models.ImageField` for `WebPImageField` — the admin
widget, `.url`, and `width_field`/`height_field` behaviour are unchanged;
`width_field`/`height_field` end up populated from the *converted* WebP's
dimensions, which is what templates use for the CLS-preventing explicit
width/height (see apps/core/templatetags/responsive_image.py).

Also cleans up orphaned files: replacing or clearing the field deletes the
previous original + its responsive variants (here, in `pre_save`); deleting
the owning row entirely is handled by a `post_delete` signal registered in
apps/core/signals.py, since Django never does either of these on its own
for a plain FileField/ImageField.
"""

from __future__ import annotations

from django.core.files.base import ContentFile
from django.db import models

from . import imaging


class WebPImageField(models.ImageField):
    def _fetch_old_value(self, model_instance) -> tuple[str | None, int | None]:
        """The field's value as currently stored in the database, before
        this save — `getattr(model_instance, ...)` only has the *new* value
        by the time `pre_save` runs, so this is the only way to know what
        (if anything) needs cleaning up after a replace/clear.
        """
        if not model_instance.pk:
            return None, None
        fields = [self.attname]
        if self.width_field:
            fields.append(self.width_field)
        row = (
            model_instance.__class__._default_manager.filter(pk=model_instance.pk)
            .values(*fields)
            .first()
        )
        if not row:
            return None, None
        return row[self.attname] or None, (row.get(self.width_field) if self.width_field else None)

    def pre_save(self, model_instance, add):
        old_name, old_width = self._fetch_old_value(model_instance)

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

        new_name = file.name if file else None
        if old_name and old_name != new_name:
            # Replaced with a different upload, or cleared entirely —
            # either way the old original + its variants are now orphaned.
            imaging.delete_with_variants(self.storage, old_name, old_width)

        return file
