"""Schemas for the /v1/outbound/render endpoint."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from .common import Warning


class RenderRequest(BaseModel):
    target_language: str
    target_channel: str | None = None
    message_type: str | None = None
    canonical_text: str
    business_refs: dict[str, Any] = Field(default_factory=dict)
    tone: str | None = None


class RenderResponse(BaseModel):
    target_language: str
    rendered_text: str
    provider: str
    postprocess: list[str] = Field(default_factory=list)
    approval_required: bool = False
    warnings: list[Warning] = Field(default_factory=list)
