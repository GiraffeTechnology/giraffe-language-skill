"""Shared, language-agnostic deterministic extraction helpers plus dispatcher.

Language-specific lexical tables live in :mod:`zh_rules`, :mod:`en_rules` and
:mod:`ja_rules`. This module owns the numeric (quantity / lead time) and
destination extraction that is common across languages, and merges everything
into a single ``field_evidence`` map.
"""

from __future__ import annotations

import re

from ..schemas.common import FieldEvidence

# --------------------------------------------------------------------------
# Cities / destinations
# --------------------------------------------------------------------------

# Bare city tokens -> canonical English city name. CJK and Latin forms.
CITY_TOKENS: dict[str, str] = {
    "东京": "Tokyo",
    "東京": "Tokyo",
    "大阪": "Osaka",
    "福岡": "Fukuoka",
    "福冈": "Fukuoka",
    "洛杉矶": "Los Angeles",
    "洛杉磯": "Los Angeles",
    "新加坡": "Singapore",
    "伦敦": "London",
    "倫敦": "London",
    "温哥华": "Vancouver",
    "溫哥華": "Vancouver",
    "tokyo": "Tokyo",
    "osaka": "Osaka",
    "fukuoka": "Fukuoka",
    "los angeles": "Los Angeles",
    "singapore": "Singapore",
    "london": "London",
    "vancouver": "Vancouver",
}

# Delivery phrases that also assert a destination. When one of these matches we
# record ``raw_rule+glossary`` as the source, mirroring the glossary entries.
DELIVERY_PHRASES: dict[str, str] = {
    "交东京": "Tokyo",
    "发东京": "Tokyo",
    "运到东京": "Tokyo",
    "东京交货": "Tokyo",
    "交大阪": "Osaka",
    "发大阪": "Osaka",
    "运到大阪": "Osaka",
    "大阪交货": "Osaka",
    "交洛杉矶": "Los Angeles",
    "发洛杉矶": "Los Angeles",
    "运到洛杉矶": "Los Angeles",
    "洛杉矶交货": "Los Angeles",
    "交洛杉磯": "Los Angeles",
    "发洛杉磯": "Los Angeles",
    "運到洛杉磯": "Los Angeles",
    "洛杉磯交貨": "Los Angeles",
    "交新加坡": "Singapore",
    "发新加坡": "Singapore",
    "运到新加坡": "Singapore",
    "新加坡交货": "Singapore",
    "交伦敦": "London",
    "发伦敦": "London",
    "运到伦敦": "London",
    "伦敦交货": "London",
    "交倫敦": "London",
    "发倫敦": "London",
    "運到倫敦": "London",
    "倫敦交貨": "London",
    "交温哥华": "Vancouver",
    "发温哥华": "Vancouver",
    "运到温哥华": "Vancouver",
    "温哥华交货": "Vancouver",
    "交溫哥華": "Vancouver",
    "发溫哥華": "Vancouver",
    "運到溫哥華": "Vancouver",
    "溫哥華交貨": "Vancouver",
    "東京納品": "Tokyo",
    "大阪納品": "Osaka",
    "福岡納品": "Fukuoka",
    "福岡へ発送": "Fukuoka",
    "福岡に発送": "Fukuoka",
    "福岡へ配送": "Fukuoka",
    "福岡に配送": "Fukuoka",
    "福岡へ納品": "Fukuoka",
    "福岡に納品": "Fukuoka",
    "福冈发货": "Fukuoka",
    "福冈交货": "Fukuoka",
}

_DESTINATION_NAME = (
    r"(?P<dest>(?:[A-Z][A-Za-z]*|[A-Z]{2,4})(?:[ -](?:[A-Z][A-Za-z]*|[A-Z]{2,4})){0,3})"
)
_DESTINATION_BOUNDARY = r"(?=\s*(?:within|in|by|,|\.|;|$|\d))"
_DESTINATION_PHRASE_RE = [
    re.compile(rf"(?i:\bto\s+be\s+(?:shipped|delivered)\s+to\s+){_DESTINATION_NAME}{_DESTINATION_BOUNDARY}"),
    re.compile(rf"(?i:\b(?:ship|shipped|shipping|deliver|delivered|delivery)\s+(?:to|into)\s+){_DESTINATION_NAME}{_DESTINATION_BOUNDARY}"),
    re.compile(rf"(?i:\bdestination\s*[:=]?\s+){_DESTINATION_NAME}{_DESTINATION_BOUNDARY}"),
    re.compile(rf"(?i:\b(?:DDP|DAP|FOB|CIF)\s+to\s+){_DESTINATION_NAME}{_DESTINATION_BOUNDARY}"),
    re.compile(rf"(?i:\bto\s+){_DESTINATION_NAME}(?i:\s+(?:within|in|by)\s+\d+)"),
]
_DESTINATION_FALSE_POSITIVES = {"be", "within", "days", "day", "pcs", "pieces", "units"}

# --------------------------------------------------------------------------
# Chinese numerals
# --------------------------------------------------------------------------

_CN_DIGIT = {
    "零": 0, "〇": 0, "一": 1, "二": 2, "两": 2, "三": 3, "四": 4,
    "五": 5, "六": 6, "七": 7, "八": 8, "九": 9,
}
_CN_UNIT = {"十": 10, "百": 100, "千": 1000}
_CN_BIG = {"万": 10000, "亿": 100000000}
_CN_CHARS = set(_CN_DIGIT) | set(_CN_UNIT) | set(_CN_BIG)

# Units that legitimately follow a Chinese numeral quantity/duration, used to
# guard inline conversion so we do not clobber unrelated characters.
_CN_NUMERAL_UNITS = "件天日枚个箱吨米"
_CN_NUMERAL_RUN = re.compile(
    rf"([{''.join(_CN_CHARS)}]+)(?=[{_CN_NUMERAL_UNITS}])"
)


def parse_chinese_numeral(text: str) -> int | None:
    """Parse a Chinese numeral string such as ``五千`` or ``四十五`` to an int."""
    if not text or any(ch not in _CN_CHARS for ch in text):
        return None
    total = 0
    section = 0
    current = 0
    for ch in text:
        if ch in _CN_DIGIT:
            current = _CN_DIGIT[ch]
        elif ch in _CN_UNIT:
            section += (current or 1) * _CN_UNIT[ch]
            current = 0
        elif ch in _CN_BIG:
            section = (section + current) * _CN_BIG[ch]
            total += section
            section = 0
            current = 0
    return total + section + current


def convert_cn_numerals_inline(text: str) -> str:
    """Replace Chinese-numeral runs that precede a unit with Arabic digits."""

    def _repl(match: re.Match[str]) -> str:
        value = parse_chinese_numeral(match.group(1))
        return str(value) if value is not None and value > 0 else match.group(1)

    return _CN_NUMERAL_RUN.sub(_repl, text)


# --------------------------------------------------------------------------
# Numeric extraction (quantity + lead time)
# --------------------------------------------------------------------------

_NUMBER_RE = re.compile(r"\d+")
_LEAD_TIME_RE = re.compile(r"(\d+)\s*(?:天内|天|日以内|日间|日|days?)", re.IGNORECASE)
_QTY_UNIT_RE = re.compile(r"^\s*(?:件|枚|个|pcs|pieces|units|ピース)", re.IGNORECASE)


def _extract_lead_time(text: str) -> tuple[FieldEvidence | None, tuple[int, int] | None]:
    match = _LEAD_TIME_RE.search(text)
    if not match:
        return None, None
    days = int(match.group(1))
    evidence = FieldEvidence(
        value=days, source="raw_rule", span=match.group(0).strip(), confidence=1.0
    )
    return evidence, match.span()


def _extract_quantity(
    text: str, lead_span: tuple[int, int] | None
) -> FieldEvidence | None:
    numbers = list(_NUMBER_RE.finditer(text))
    candidates = []
    for m in numbers:
        if lead_span and not (m.end() <= lead_span[0] or m.start() >= lead_span[1]):
            continue  # overlaps the lead-time number
        candidates.append(m)
    if not candidates:
        return None

    # Prefer a number that is immediately followed by an explicit unit.
    for m in candidates:
        if _QTY_UNIT_RE.match(text[m.end():]):
            unit_match = _QTY_UNIT_RE.match(text[m.end():])
            span = text[m.start():m.end() + (unit_match.end() if unit_match else 0)]
            return FieldEvidence(
                value=int(m.group(0)), source="raw_rule", span=span.strip(), confidence=1.0
            )

    first = candidates[0]
    return FieldEvidence(
        value=int(first.group(0)), source="raw_rule", span=first.group(0), confidence=0.9
    )


def _canonical_destination_phrase(value: str) -> str | None:
    cleaned = value.strip(" .,;:()[]{}\n\t")
    if not cleaned:
        return None
    if cleaned.lower() in _DESTINATION_FALSE_POSITIVES:
        return None
    return cleaned.upper() if cleaned.isupper() and len(cleaned) <= 4 else cleaned.title()


def _extract_destination(text: str) -> FieldEvidence | None:
    # Delivery phrases first (they carry an explicit "deliver to" intent).
    for phrase, city in DELIVERY_PHRASES.items():
        if phrase in text:
            return FieldEvidence(
                value=city, source="raw_rule+glossary", span=phrase, confidence=1.0
            )

    for pattern in _DESTINATION_PHRASE_RE:
        match = pattern.search(text)
        if not match:
            continue
        destination = _canonical_destination_phrase(match.group("dest"))
        if destination:
            return FieldEvidence(
                value=destination,
                source="raw_rule",
                span=match.group("dest").strip(),
                confidence=0.92,
            )

    lowered = text.lower()
    for token, city in CITY_TOKENS.items():
        needle = token.lower()
        if needle in lowered:
            return FieldEvidence(value=city, source="raw_rule", span=token, confidence=0.95)
    return None


# --------------------------------------------------------------------------
# Lexical matching helper (used by language modules)
# --------------------------------------------------------------------------


def match_single(
    text: str, table: list[tuple[str, str]], *, source: str,
    confidence: float, lowercase: bool = False
) -> FieldEvidence | None:
    """Return evidence for the first matching term in ``table``.

    ``table`` is a list of (source_token, canonical_value) pairs, expected to be
    ordered longest-first so compound terms win. ``lowercase`` enables
    case-insensitive matching for Latin-script tokens.
    """
    haystack = text.lower() if lowercase else text
    for token, value in table:
        needle = token.lower() if lowercase else token
        if needle and needle in haystack:
            return FieldEvidence(value=value, source=source, span=token, confidence=confidence)
    return None


def match_multi(
    text: str, table: list[tuple[str, str]], *, source: str,
    confidence: float, lowercase: bool = False
) -> FieldEvidence | None:
    """Collect all matching canonical values from ``table`` into a list value."""
    haystack = text.lower() if lowercase else text
    values: list[str] = []
    spans: list[str] = []
    for token, value in table:
        needle = token.lower() if lowercase else token
        if needle and needle in haystack and value not in values:
            values.append(value)
            spans.append(token)
    if not values:
        return None
    return FieldEvidence(
        value=values, source=source, span=" ".join(spans), confidence=confidence
    )


def order_longest_first(table: dict[str, str]) -> list[tuple[str, str]]:
    """Return dict items ordered by descending key length."""
    return sorted(table.items(), key=lambda kv: len(kv[0]), reverse=True)


# --------------------------------------------------------------------------
# Dispatcher
# --------------------------------------------------------------------------


def extract_raw(text: str, language: str) -> dict[str, FieldEvidence]:
    """Extract deterministic field evidence from ``text`` for ``language``.

    Returns a mapping of field name to :class:`FieldEvidence`. Numeric and
    destination fields are handled here; lexical fields (garment, modifiers,
    fabric, color, gender, quality, intent) come from the language module.
    """
    from . import en_rules, ja_rules, zh_rules

    # Inline-convert Chinese numerals (e.g. 五千件 -> 5000件) for zh inputs.
    working = convert_cn_numerals_inline(text) if language == "zh" else text

    evidence: dict[str, FieldEvidence] = {}

    lead_ev, lead_span = _extract_lead_time(working)
    if lead_ev is not None:
        evidence["lead_time_days"] = lead_ev

    qty_ev = _extract_quantity(working, lead_span)
    if qty_ev is not None:
        evidence["quantity"] = qty_ev
        evidence["quantity_unit"] = FieldEvidence(
            value="pcs", source="raw_rule", span=qty_ev.span, confidence=0.9
        )

    dest_ev = _extract_destination(working)
    if dest_ev is not None:
        evidence["destination"] = dest_ev

    lexical_module = {"zh": zh_rules, "ja": ja_rules}.get(language, en_rules)
    evidence.update(lexical_module.extract_lexical(text))
    return evidence


def gather_evidence(
    raw_text: str,
    canonical_text: str | None = None,
    provided: dict[str, FieldEvidence] | None = None,
) -> tuple[dict[str, FieldEvidence], str]:
    """Gather merged field evidence for structuring.

    Runs deterministic extraction on the raw text, backfills any fields not
    found there from the canonical English text, then lets caller-provided
    evidence (e.g. from a prior /v1/inbound/normalize call) take precedence.

    Returns ``(evidence, detected_language)``.
    """
    from ..language.detector import detect_language

    detected = detect_language(raw_text).detected
    evidence = extract_raw(raw_text, detected)

    if canonical_text:
        canon_evidence = extract_raw(canonical_text, "en")
        for key, value in canon_evidence.items():
            evidence.setdefault(key, value)

    if provided:
        evidence.update(provided)

    return evidence, detected
