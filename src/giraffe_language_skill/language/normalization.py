"""Lightweight text normalization applied before extraction/translation."""

from __future__ import annotations

import unicodedata

# Full-width → half-width digit map so "５０００件" behaves like "5000件".
_FULLWIDTH_DIGITS = {ord("０") + i: ord("0") + i for i in range(10)}
# Full-width Latin letters and common full-width punctuation collapse via NFKC.


def normalize_text(text: str) -> str:
    """Return a normalized copy of ``text``.

    - Applies NFKC normalization (folds full-width Latin/space forms).
    - Maps full-width digits to ASCII digits.
    - Collapses runs of ASCII whitespace and strips ends.

    CJK punctuation such as ``，`` and ``。`` is preserved because downstream
    extractors and glossary phrases may rely on it.
    """
    if not text:
        return ""
    text = text.translate(_FULLWIDTH_DIGITS)
    # NFKC would turn CJK commas into ASCII in some locales; guard by only
    # normalizing compatibility forms of digits/letters, not punctuation.
    normalized = "".join(
        unicodedata.normalize("NFKC", ch) if ch.isalnum() else ch for ch in text
    )
    # Collapse ASCII whitespace runs but keep single spaces meaningful.
    normalized = " ".join(normalized.split(" "))
    return normalized.strip()
