"""Schemas for the /v1/translate endpoint."""

from __future__ import annotations

from pydantic import BaseModel, Field

from .common import Warning


class TranslateRequest(BaseModel):
    source_text: str
    source_language: str = "auto"
    target_language: str = "en"
    domain_hint: str | None = None


class TranslateResponse(BaseModel):
    source_language: str
    target_language: str
    translated_text: str
    provider: str
    model: str
    warnings: list[Warning] = Field(default_factory=list)
