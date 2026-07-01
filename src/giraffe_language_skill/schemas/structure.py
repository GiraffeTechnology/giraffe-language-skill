"""Schemas for the /v1/structure/* endpoints."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from .common import FieldEvidenceMap, ValidationStatus, Warning


class StructureRequest(BaseModel):
    raw_text: str
    canonical_text: str | None = None
    field_evidence: FieldEvidenceMap = Field(default_factory=dict)
    schema_version: str | None = None


class StructureResponse(BaseModel):
    # Attribute is renamed to avoid shadowing BaseModel.schema; the wire key
    # remains "schema" via the alias.
    model_config = ConfigDict(populate_by_name=True)

    result_schema: str = Field(alias="schema")
    validation_status: ValidationStatus
    structured: dict[str, Any]
    missing_fields: list[str] = Field(default_factory=list)
    confidence_score: float = Field(ge=0.0, le=1.0)
    field_sources: dict[str, str] = Field(default_factory=dict)
    warnings: list[Warning] = Field(default_factory=list)
