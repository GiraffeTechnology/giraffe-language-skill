"""Schemas for the /v1/inbound/normalize endpoint."""

from __future__ import annotations

from pydantic import BaseModel, Field

from .common import FieldEvidenceMap, LanguageDetection, Warning


class ConversationContext(BaseModel):
    tenant_id: str = "default"
    sender_role: str | None = None


class NormalizeRequest(BaseModel):
    source_text: str
    source_language: str = "auto"
    canonical_language: str = "en"
    domain_hint: str | None = None
    source_channel: str | None = None
    conversation_context: ConversationContext = Field(default_factory=ConversationContext)


class TranslationMeta(BaseModel):
    provider: str
    model: str
    glossary_version: str


class NormalizeResponse(BaseModel):
    raw_text: str
    language: LanguageDetection
    canonical_language: str
    canonical_text: str
    field_evidence: FieldEvidenceMap = Field(default_factory=dict)
    translation: TranslationMeta
    warnings: list[Warning] = Field(default_factory=list)
