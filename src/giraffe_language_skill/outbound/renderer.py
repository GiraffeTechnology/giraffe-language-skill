"""Render a canonical English outbound packet into a target-language message."""

from __future__ import annotations

import re

from ..glossary import GlossaryMatcher
from ..schemas.common import Warning, WarningCode
from ..schemas.render import RenderRequest, RenderResponse
from ..translation.base import SUPPORTED_PAIRS
from .channel_formatting import format_for_channel
from .templates import RULES


def _apply_rules(text: str, target_language: str) -> str:
    for pattern, replacement in RULES.get(target_language, []):
        if callable(replacement):
            text = pattern.sub(replacement, text)
        else:
            text = pattern.sub(replacement, text)
    return text


def render_outbound(
    request: RenderRequest,
    glossary: GlossaryMatcher | None = None,
    provider_name: str = "mock",
) -> RenderResponse:
    """Render ``request.canonical_text`` into ``request.target_language``."""
    glossary = glossary or GlossaryMatcher()
    warnings: list[Warning] = []
    target = request.target_language
    postprocess: list[str] = []

    text = request.canonical_text

    if target == "en":
        # Canonical language is English; no translation needed.
        rendered = re.sub(r"\s+", " ", text).strip()
        return RenderResponse(
            target_language=target,
            rendered_text=rendered,
            provider=provider_name,
            postprocess=["passthrough"],
            approval_required=_approval_required(request),
            warnings=warnings,
        )

    if f"en-{target}" not in SUPPORTED_PAIRS:
        warnings.append(
            Warning(
                code=WarningCode.UNSUPPORTED_LANGUAGE_PAIR,
                message=f"Outbound rendering not supported for en-{target}.",
            )
        )

    # 1) Deterministic rewrite rules (reordering, units, delivery phrasing).
    text = _apply_rules(text, target)
    # 2) Glossary substitution for any remaining known phrases.
    text = glossary.substitute(text, "en", target)
    postprocess.append("glossary")
    # 3) Channel + CJK spacing cleanup.
    text = format_for_channel(text, request.target_channel, target)
    postprocess.append("channel_formatting")

    return RenderResponse(
        target_language=target,
        rendered_text=text,
        provider=provider_name,
        postprocess=postprocess,
        approval_required=_approval_required(request),
        warnings=warnings,
    )


def _approval_required(request: RenderRequest) -> bool:
    if "approval" in request.canonical_text.lower():
        return True
    if request.message_type and "approval" in request.message_type.lower():
        return True
    return False
