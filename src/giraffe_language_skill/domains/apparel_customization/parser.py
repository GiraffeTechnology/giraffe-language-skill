"""Apparel customization parser: canonical packet -> structured fields."""

from __future__ import annotations

from ...config import get_settings
from ...extractors import gather_evidence
from ...schemas.common import FieldEvidence
from ...schemas.structure import StructureResponse
from .schema import SCHEMA_VERSION, ApparelCustomizationFields
from .validator import validate_apparel


def _val(evidence: dict[str, FieldEvidence], key: str):
    ev = evidence.get(key)
    return ev.value if ev else None


def _confidence(evidence: dict[str, FieldEvidence], completeness: float) -> float:
    present = [ev.confidence for ev in evidence.values()]
    mean = sum(present) / len(present) if present else 0.0
    return round(mean * completeness, 2)


def structure_apparel_customization(
    raw_text: str,
    canonical_text: str | None = None,
    provided_evidence: dict[str, FieldEvidence] | None = None,
) -> StructureResponse:
    settings = get_settings()
    evidence, _lang = gather_evidence(raw_text, canonical_text, provided_evidence)

    fields = ApparelCustomizationFields(
        garment_type=_val(evidence, "garment_type"),
        fabric=_val(evidence, "fabric"),
        color=_val(evidence, "color"),
        gender=_val(evidence, "gender"),
        quantity=_val(evidence, "quantity"),
        delivery_destination=_val(evidence, "destination"),
        delivery_deadline=None,
        customization_notes=[],
    )

    structured = fields.to_ordered_dict()
    status, missing = validate_apparel(structured, settings.require_critical_fields)

    total_critical = 3
    satisfied = total_critical - len(missing)
    completeness = satisfied / total_critical if total_critical else 1.0
    confidence = _confidence(evidence, completeness)

    field_sources: dict[str, str] = {}
    # Map canonical structured keys back to evidence provenance.
    key_to_evidence = {
        "garment_type": "garment_type",
        "fabric": "fabric",
        "color": "color",
        "gender": "gender",
        "quantity": "quantity",
        "delivery_destination": "destination",
    }
    for out_key, ev_key in key_to_evidence.items():
        ev = evidence.get(ev_key)
        if ev is not None and structured.get(out_key) is not None:
            field_sources[out_key] = ev.source

    return StructureResponse(
        schema=SCHEMA_VERSION,
        validation_status=status,
        structured=structured,
        missing_fields=missing,
        confidence_score=confidence,
        field_sources=field_sources,
    )
