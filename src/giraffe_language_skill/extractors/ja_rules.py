"""Japanese (ja) lexical extraction tables and rules."""

from __future__ import annotations

from ..schemas.common import FieldEvidence
from . import raw_rules as rr

GARMENTS: dict[str, tuple[str, str]] = {
    "シャツ": ("shirt", "apparel"),
}
STYLE_MODIFIERS: dict[str, str] = {"チェック柄": "plaid", "チェック": "plaid"}
FABRICS: dict[str, str] = {"綿": "cotton", "コットン": "cotton", "ポリエステル": "polyester"}
COLORS: dict[str, str] = {"白": "white", "黒": "black", "青": "blue"}
GENDERS: dict[str, str] = {"メンズ": "men", "男性": "men", "レディース": "women", "女性": "women"}
QUALITY: dict[str, str] = {"高品質": "high", "高級": "high"}
INTENT: list[tuple[str, str]] = [
    ("見積", "quotation"),
    ("納期", "lead_time_inquiry"),
]


def _garment(text: str) -> tuple[FieldEvidence | None, FieldEvidence | None]:
    for token, (english, category) in rr.order_longest_first(GARMENTS):
        if token in text:
            garment_ev = FieldEvidence(value=english, source="glossary", span=token, confidence=0.95)
            category_ev = FieldEvidence(
                value=category, source="glossary", span=token, confidence=0.9
            )
            return garment_ev, category_ev
    return None, None


def _intent(text: str) -> FieldEvidence | None:
    for token, value in INTENT:
        if token in text:
            return FieldEvidence(value=value, source="raw_rule", span=token, confidence=0.85)
    return None


def extract_lexical(text: str) -> dict[str, FieldEvidence]:
    evidence: dict[str, FieldEvidence] = {}

    garment_ev, category_ev = _garment(text)
    if garment_ev is not None:
        evidence["garment_type"] = garment_ev
        evidence["product_category"] = category_ev

    modifiers = rr.match_multi(
        text, rr.order_longest_first(STYLE_MODIFIERS), source="glossary", confidence=0.9
    )
    if modifiers is not None:
        evidence["product_modifier"] = modifiers

    for field, table, conf in (
        ("fabric", FABRICS, 0.9),
        ("color", COLORS, 0.9),
        ("gender", GENDERS, 0.9),
        ("quality_level", QUALITY, 0.9),
    ):
        ev = rr.match_single(text, rr.order_longest_first(table), source="glossary", confidence=conf)
        if ev is not None:
            evidence[field] = ev

    intent_ev = _intent(text)
    if intent_ev is not None:
        evidence["intent"] = intent_ev

    return evidence
