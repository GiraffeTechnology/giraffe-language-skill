"""Inbound normalization route: multilingual message -> canonical packet."""

from __future__ import annotations

from fastapi import APIRouter

from ..config import get_settings
from ..extractors import extract_raw
from ..glossary import GlossaryMatcher
from ..language import detect_language, normalize_text
from ..schemas.common import Warning, WarningCode
from ..schemas.normalize import NormalizeRequest, NormalizeResponse, TranslationMeta
from ..translation.base import get_translation_provider

router = APIRouter(prefix="/v1/inbound", tags=["inbound"])

# Below this detection confidence we attach a low-confidence warning.
_LOW_CONFIDENCE = 0.5


@router.post("/normalize", response_model=NormalizeResponse)
def normalize(request: NormalizeRequest) -> NormalizeResponse:
    settings = get_settings()
    glossary = GlossaryMatcher()
    provider = get_translation_provider(settings)
    warnings: list[Warning] = []

    raw_text = request.source_text
    cleaned = normalize_text(raw_text)

    language = detect_language(cleaned, request.source_language)
    if language.confidence < _LOW_CONFIDENCE:
        warnings.append(
            Warning(
                code=WarningCode.LANGUAGE_DETECTION_LOW_CONFIDENCE,
                message=f"Low confidence ({language.confidence}) detecting language.",
            )
        )

    canonical_language = request.canonical_language or settings.canonical_language

    # Deterministic field extraction happens on the raw text and is the source
    # of truth for explicit business facts — never the translation.
    field_evidence = extract_raw(cleaned, language.detected)

    if language.detected == canonical_language:
        canonical_text = cleaned
        translation_warnings: list[Warning] = []
        provider_name, model_name = provider.name, "passthrough"
    else:
        result = provider.translate(
            cleaned, language.detected, canonical_language, request.domain_hint
        )
        canonical_text = result.translated_text
        translation_warnings = result.warnings
        provider_name, model_name = result.provider, result.model

    warnings.extend(translation_warnings)

    return NormalizeResponse(
        raw_text=raw_text,
        language=language,
        canonical_language=canonical_language,
        canonical_text=canonical_text,
        field_evidence=field_evidence,
        translation=TranslationMeta(
            provider=provider_name,
            model=model_name,
            glossary_version=glossary.version,
        ),
        warnings=warnings,
    )
