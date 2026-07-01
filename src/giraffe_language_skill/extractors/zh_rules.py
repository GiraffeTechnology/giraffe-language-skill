"""Chinese (zh) lexical extraction tables and rules."""

from __future__ import annotations

from ..schemas.common import FieldEvidence
from . import raw_rules as rr

# token -> (english garment, product category)
GARMENTS: dict[str, tuple[str, str]] = {
    "衬衫": ("shirt", "apparel"),
    "衬衣": ("shirt", "apparel"),
}
STYLE_MODIFIERS: dict[str, str] = {"格子": "plaid"}
FABRICS: dict[str, str] = {"纯棉": "cotton", "棉": "cotton", "涤纶": "polyester"}
COLORS: dict[str, str] = {"白色": "white", "黑色": "black", "蓝色": "blue"}
GENDERS: dict[str, str] = {
    "男款": "men", "男装": "men", "男": "men",
    "女款": "women", "女装": "women", "女": "women",
}
QUALITY: dict[str, str] = {"高品质": "high", "高质量": "high", "顶级": "high"}
# Ordered by precedence (checked in list order).
INTENT: list[tuple[str, str]] = [
    ("初步报价", "preliminary_quote"),
    ("我要定制", "customize"),
    ("定制", "customize"),
    ("询价", "inquiry"),
    ("报价", "quote"),
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
            return FieldEvidence(value=value, source="raw_rule", span=token, confidence=0.9)
    return None


def extract_lexical(text: str) -> dict[str, FieldEvidence]:
    evidence: dict[str, FieldEvidence] = {}

    garment_ev, category_ev = _garment(text)
    if garment_ev is not None:
        evidence["garment_type"] = garment_ev
        evidence["product_category"] = category_ev

    modifiers = rr.match_multi(
        text, rr.order_longest_first(STYLE_MODIFIERS), source="glossary", confidence=0.95
    )
    if modifiers is not None:
        evidence["product_modifier"] = modifiers

    for field, table, conf in (
        ("fabric", FABRICS, 0.95),
        ("color", COLORS, 0.95),
        ("gender", GENDERS, 0.95),
        ("quality_level", QUALITY, 0.95),
    ):
        ev = rr.match_single(text, rr.order_longest_first(table), source="glossary", confidence=conf)
        if ev is not None:
            evidence[field] = ev

    intent_ev = _intent(text)
    if intent_ev is not None:
        evidence["intent"] = intent_ev

    return evidence
