"""Gates whether the *current* page is indexable in the *current* language —
not just whether hreflang should advertise it. Without this, a language
variant with no translation_complete_<lang> flag still rendered
`index, follow` and was reachable via the language switcher and any guessed
URL, so Google could crawl and index the same page structure carrying
literal "TODO: content needed" text — duplicate/thin content per
https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls,
even though it was correctly excluded from hreflang and (for most models)
the sitemap.
"""

from __future__ import annotations

from django import template
from django.utils import translation

register = template.Library()


@register.filter
def lang_indexable(obj, allowed_langs: str = "") -> bool:
    """Usage: {{ obj|lang_indexable }} or {{ obj|lang_indexable:"en,ru" }}.

    English is always indexable. Any other language must both be in
    `allowed_langs` (when given) and have translation_complete_<lang>=True
    on `obj`.
    """
    lang = translation.get_language()
    if allowed_langs:
        allowed = {code.strip() for code in allowed_langs.split(",")}
        if lang not in allowed:
            return False
    if lang == "en":
        return True
    return bool(getattr(obj, f"translation_complete_{lang}", False))
