"""Structuring routes for trade RFQ and apparel customization."""

from __future__ import annotations

from fastapi import APIRouter

from ..domains.apparel_customization import structure_apparel_customization
from ..domains.trade_rfq import structure_rfq
from ..schemas.structure import StructureRequest, StructureResponse

router = APIRouter(prefix="/v1/structure", tags=["structure"])


@router.post("/rfq", response_model=StructureResponse)
def structure_rfq_route(request: StructureRequest) -> StructureResponse:
    return structure_rfq(
        raw_text=request.raw_text,
        canonical_text=request.canonical_text,
        provided_evidence=request.field_evidence or None,
    )


@router.post("/apparel-customization", response_model=StructureResponse)
def structure_apparel_route(request: StructureRequest) -> StructureResponse:
    return structure_apparel_customization(
        raw_text=request.raw_text,
        canonical_text=request.canonical_text,
        provided_evidence=request.field_evidence or None,
    )
