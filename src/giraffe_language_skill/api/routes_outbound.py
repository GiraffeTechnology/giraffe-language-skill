"""Outbound rendering route."""

from __future__ import annotations

from fastapi import APIRouter

from ..config import get_settings
from ..outbound import render_outbound
from ..schemas.render import RenderRequest, RenderResponse
from ..translation.base import get_translation_provider

router = APIRouter(prefix="/v1/outbound", tags=["outbound"])


@router.post("/render", response_model=RenderResponse)
def render(request: RenderRequest) -> RenderResponse:
    provider = get_translation_provider(get_settings())
    return render_outbound(request, provider_name=provider.name)
