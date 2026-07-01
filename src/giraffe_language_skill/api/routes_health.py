"""Health check route."""

from __future__ import annotations

from fastapi import APIRouter

from .. import SERVICE_NAME, __version__

router = APIRouter(tags=["health"])


@router.get("/healthz")
def healthz() -> dict:
    return {"ok": True, "service": SERVICE_NAME, "version": __version__}
