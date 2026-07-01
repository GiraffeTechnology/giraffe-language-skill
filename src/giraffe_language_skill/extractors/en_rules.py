"""English (en) lexical extraction tables and rules.

English is both a source language (en -> en normalization) and the canonical
language, so these rules also run when structuring already-English input.
"""

from __future__ import annotations

from ..schemas.common import FieldEvidence
from . import raw_rules as rr

GARMENTS: dict[str, tuple[str, str]] = {
    "shirts": ("shirt", "apparel"),
    "shirt": ("shirt", "apparel"),
    "blouses": ("blouse", "apparel"),
    "blouse": ("blouse", "apparel"),
}
STYLE_MODIFIERS: dict[str, str] = {"plaid": "plaid", "striped": "striped", "checked": "plaid"}
FABRICS: dict[str, str] = {"cotton": "cotton", "polyester": "polyester", "linen": "linen"}
COLORS: dict[str, str] = {"white": "white", "black": "black", "blue": "blue"}
GENDERS: dict[str, str] = {
    "men's": "men", "mens": "men", "men": "men",
    "women's": "women", "womens": "women", "women": "women",
}
QUALITY: dict[str, str] = {"high-quality": "high", "high quality": "high", "premium": "high"}
INTENT: list[tuple[str, str]] = [
    ("preliminary quote", "preliminary_quote"),
    ("customize", "customize"),
    ("inquiry", "inquiry"),
    ("quote", "quote"),
    ("order", "order"),
]


def _garment(text: str) -> tuple[FieldEvidence | None, FieldEvidence | None]:
    lowered = text.lower()
    for token, (english, category) in rr.order_longest_first(GARMENTS):
        if token in lowered:
            garment_ev = FieldEvidence(
                value=english, source="canonical_parser", span=token, confidence=0.95
            )
            category_ev = FieldEvidence(
                value=category, source="canonical_parser", span=token, confidence=0.9
            )
            return garment_ev, category_ev
    return None, None


def _intent(text: str) -> FieldEvidence | None:
    lowered = text.lower()
    for token, value in INTENT:
        if token in lowered:
            return FieldEvidence(value=value, source="raw_rule", span=token, confidence=0.85)
    return None


def extract_lexical(text: str) -> dict[str, FieldEvidence]:
    evidence: dict[str, FieldEvidence] = {}

    garment_ev, category_ev = _garment(text)
    if garment_ev is not None:
        evidence["garment_type"] = garment_ev
        evidence["product_category"] = category_ev

    modifiers = rr.match_multi(
        text, rr.order_longest_first(STYLE_MODIFIERS),
        source="canonical_parser", confidence=0.9, lowercase=True,
    )
    if modifiers is not None:
        evidence["product_modifier"] = modifiers

    for field, table, conf in (
        ("fabric", FABRICS, 0.9),
        ("color", COLORS, 0.9),
        ("gender", GENDERS, 0.9),
        ("quality_level", QUALITY, 0.9),
    ):
        ev = rr.match_single(
            text, rr.order_longest_first(table), source="canonical_parser",
            confidence=conf, lowercase=True,
        )
        if ev is not None:
            evidence[field] = ev

    intent_ev = _intent(text)
    if intent_ev is not None:
        evidence["intent"] = intent_ev

    return evidence
