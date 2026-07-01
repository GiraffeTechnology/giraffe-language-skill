"""Validation gate for apparel customization structuring."""

from __future__ import annotations

from typing import Any

from ...schemas.common import ValidationStatus
from .schema import CRITICAL_FIELDS


def _is_present(structured: dict[str, Any], field: object) -> bool:
    if isinstance(field, tuple):
        return any(_is_present(structured, alt) for alt in field)
    value = structured.get(field)  # type: ignore[arg-type]
    if value is None:
        return False
    if isinstance(value, (list, str)) and len(value) == 0:
        return False
    return True


def validate_apparel(
    structured: dict[str, Any], require_critical: bool = True
) -> tuple[ValidationStatus, list[str]]:
    missing: list[str] = []
    for field in CRITICAL_FIELDS:
        if not _is_present(structured, field):
            primary = field[0] if isinstance(field, tuple) else field
            missing.append(str(primary))

    if not missing:
        return ValidationStatus.VALID, []
    if require_critical:
        return ValidationStatus.NEEDS_CONFIRMATION, missing
    return ValidationStatus.VALID, missing
