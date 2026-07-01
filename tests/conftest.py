"""Shared test fixtures. Tests never require network or model downloads."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from giraffe_language_skill.api.main import create_app


@pytest.fixture(scope="session")
def client() -> TestClient:
    return TestClient(create_app())
