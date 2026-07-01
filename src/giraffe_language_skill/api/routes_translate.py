"""Translation route."""

from __future__ import annotations

from fastapi import APIRouter

from ..config import get_settings
from ..language import detect_language, normalize_text
from ..schemas.translate import TranslateRequest, TranslateResponse
from ..translation.base import get_translation_provider

router = APIRouter(prefix="/v1", tags=["translate"])


@router.post("/translate", response_model=TranslateResponse)
def translate(request: TranslateRequest) -> TranslateResponse:
    settings = get_settings()
    provider = get_translation_provider(settings)

    cleaned = normalize_text(request.source_text)
    source_language = request.source_language
    if not source_language or source_language == "auto":
        source_language = detect_language(cleaned).detected

    result = provider.translate(
        cleaned, source_language, request.target_language, request.domain_hint
    )

    return TranslateResponse(
        source_language=source_language,
        target_language=request.target_language,
        translated_text=result.translated_text,
        provider=result.provider,
        model=result.model,
        warnings=result.warnings,
    )
