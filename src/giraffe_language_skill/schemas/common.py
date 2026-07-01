"""Shared schema types and enums used across endpoints."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ValidationStatus(str, Enum):
    """Outcome of a structuring validation gate."""

    VALID = "valid"
    NEEDS_CONFIRMATION = "needs_confirmation"
    BLOCKED = "blocked"
    FAILED = "failed"


class WarningCode(str, Enum):
    """Typed warning / error codes returned instead of opaque backend errors."""

    LANGUAGE_DETECTION_LOW_CONFIDENCE = "LANGUAGE_DETECTION_LOW_CONFIDENCE"
    TRANSLATION_PROVIDER_UNAVAILABLE = "TRANSLATION_PROVIDER_UNAVAILABLE"
    TRANSLATION_MODEL_MISSING = "TRANSLATION_MODEL_MISSING"
    TRANSLATION_FAILED = "TRANSLATION_FAILED"
    STRUCTURING_FAILED = "STRUCTURING_FAILED"
    CRITICAL_FIELD_MISSING = "CRITICAL_FIELD_MISSING"
    UNSUPPORTED_LANGUAGE_PAIR = "UNSUPPORTED_LANGUAGE_PAIR"
    GLOSSARY_LOAD_FAILED = "GLOSSARY_LOAD_FAILED"


class Warning(BaseModel):
    """A single non-fatal warning attached to a response."""

    code: WarningCode
    message: str
    field: str | None = None


class LanguageDetection(BaseModel):
    """Detected language and confidence for a piece of text."""

    detected: str
    confidence: float = Field(ge=0.0, le=1.0)


class FieldEvidence(BaseModel):
    """Evidence backing a single extracted field.

    ``source`` records provenance, e.g. ``raw_rule``, ``glossary`` or
    ``raw_rule+glossary``. ``span`` is the substring of the original raw text
    that produced the value, preserved so downstream products never have to
    trust a translation for explicit business facts.
    """

    value: Any
    source: str
    span: str | None = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


FieldEvidenceMap = dict[str, FieldEvidence]
