"""FastAPI application entrypoint and CLI runner."""

from __future__ import annotations

import argparse

from fastapi import FastAPI

from .. import SERVICE_NAME, __version__
from ..config import get_settings
from . import (
    routes_health,
    routes_inbound,
    routes_models,
    routes_outbound,
    routes_structure,
    routes_translate,
)


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    app = FastAPI(
        title="Giraffe Language Skill Layer",
        version=__version__,
        description=(
            "Standalone multilingual canonicalization, deterministic extraction "
            "and local translation service for Giraffe products."
        ),
    )
    app.include_router(routes_health.router)
    app.include_router(routes_models.router)
    app.include_router(routes_inbound.router)
    app.include_router(routes_translate.router)
    app.include_router(routes_structure.router)
    app.include_router(routes_outbound.router)
    return app


app = create_app()


def run() -> None:
    """Console-script / ``python -m`` entrypoint."""
    parser = argparse.ArgumentParser(
        prog=f"python -m {SERVICE_NAME.replace('-', '_')}.api.main",
        description=f"Run the {SERVICE_NAME} FastAPI service.",
    )
    settings = get_settings()
    parser.add_argument("--host", default=settings.host, help="Bind host.")
    parser.add_argument("--port", type=int, default=settings.port, help="Bind port.")
    parser.add_argument(
        "--reload", action="store_true", help="Enable auto-reload (development)."
    )
    args = parser.parse_args()

    import uvicorn

    uvicorn.run(
        "giraffe_language_skill.api.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )


if __name__ == "__main__":
    run()
