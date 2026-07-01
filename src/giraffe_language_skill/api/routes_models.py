"""Model / capability discovery route."""

from __future__ import annotations

from fastapi import APIRouter

from ..config import get_settings
from ..translation.base import get_translation_provider
from ..translation.model_registry import available_language_pairs

router = APIRouter(prefix="/v1", tags=["models"])


@router.get("/models")
def list_models() -> dict:
    settings = get_settings()
    provider = get_translation_provider(settings)
    return {
        "provider": provider.name,
        "canonical_language": settings.canonical_language,
        "available_language_pairs": available_language_pairs(),
        "models": provider.available_models(),
    }
