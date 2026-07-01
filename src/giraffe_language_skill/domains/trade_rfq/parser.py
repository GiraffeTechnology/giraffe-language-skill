"""Trade RFQ parser: canonical packet -> structured, validated RFQ fields."""

from __future__ import annotations

from ...config import get_settings
from ...extractors import gather_evidence
from ...schemas.common import FieldEvidence
from ...schemas.structure import StructureResponse
from .schema import SCHEMA_VERSION, TradeRFQFields
from .validator import validate_rfq


def _compose_product_name(
    modifiers: list[str], garment: str | None
) -> str | None:
    if garment:
        parts = [*modifiers, garment] if modifiers else [garment]
        return " ".join(parts)
    return None


def _confidence(evidence: dict[str, FieldEvidence], completeness: float) -> float:
    present = [ev.confidence for ev in evidence.values()]
    mean = sum(present) / len(present) if present else 0.0
    return round(mean * completeness, 2)


def structure_rfq(
    raw_text: str,
    canonical_text: str | None = None,
    provided_evidence: dict[str, FieldEvidence] | None = None,
) -> StructureResponse:
    """Structure a trade RFQ from raw + canonical text."""
    settings = get_settings()
    evidence, _lang = gather_evidence(raw_text, canonical_text, provided_evidence)

    modifiers_ev = evidence.get("product_modifier")
    modifiers = list(modifiers_ev.value) if modifiers_ev else []
    garment_ev = evidence.get("garment_type")
    garment = garment_ev.value if garment_ev else None

    fields = TradeRFQFields(
        quantity=_val(evidence, "quantity"),
        quantity_unit=_val(evidence, "quantity_unit") or "pcs",
        product_name=_compose_product_name(modifiers, garment),
        product_category=_val(evidence, "product_category"),
        product_modifier=modifiers,
        destination=_val(evidence, "destination"),
        lead_time_days=_val(evidence, "lead_time_days"),
        quality_level=_val(evidence, "quality_level"),
        intent=_val(evidence, "intent") or ("preliminary_quote" if _val(evidence, "quantity") else None),
    )

    structured = fields.to_ordered_dict()
    status, missing = validate_rfq(structured, settings.require_critical_fields)

    total_critical = 4
    satisfied = total_critical - len(missing)
    completeness = satisfied / total_critical if total_critical else 1.0
    confidence = _confidence(evidence, completeness)

    field_sources = _field_sources(evidence, structured)

    return StructureResponse(
        schema=SCHEMA_VERSION,
        validation_status=status,
        structured=structured,
        missing_fields=missing,
        confidence_score=confidence,
        field_sources=field_sources,
    )


def _val(evidence: dict[str, FieldEvidence], key: str):
    ev = evidence.get(key)
    return ev.value if ev else None


def _field_sources(
    evidence: dict[str, FieldEvidence], structured: dict
) -> dict[str, str]:
    sources: dict[str, str] = {}
    for key in structured:
        ev = evidence.get(key)
        if ev is not None:
            sources[key] = ev.source
    # product_name is composed from garment + modifiers.
    if structured.get("product_name"):
        sources["product_name"] = "canonical_parser+glossary"
    return sources
