"""Service configuration loaded from environment variables.

All settings default to values that let tests and local API smoke run without
model downloads or network access. In particular the translation provider
defaults to ``mock``.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Repository root (…/giraffe-language-skill). Used to resolve the default
# glossary path relative to the installed package regardless of CWD.
_PACKAGE_DIR = Path(__file__).resolve().parent
_DEFAULT_GLOSSARY = _PACKAGE_DIR / "glossary" / "giraffe_trade_glossary.yml"


class Settings(BaseSettings):
    """Runtime settings.

    Each field is bound to its explicit environment variable name via
    ``validation_alias`` because the variables do not share a single common
    prefix.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    host: str = Field(default="127.0.0.1", validation_alias="GIRAFFE_LANGUAGE_SKILL_HOST")
    port: int = Field(default=8788, validation_alias="GIRAFFE_LANGUAGE_SKILL_PORT")
    canonical_language: str = Field(
        default="en", validation_alias="GIRAFFE_LANGUAGE_CANONICAL_LANGUAGE"
    )

    translation_provider: str = Field(
        default="mock", validation_alias="GIRAFFE_TRANSLATION_PROVIDER"
    )
    translation_model_dir: str = Field(
        default="./models", validation_alias="GIRAFFE_TRANSLATION_MODEL_DIR"
    )
    translation_device: str = Field(
        default="cpu", validation_alias="GIRAFFE_TRANSLATION_DEVICE"
    )
    translation_compute_type: str = Field(
        default="int8", validation_alias="GIRAFFE_TRANSLATION_COMPUTE_TYPE"
    )
    translation_cache_enabled: bool = Field(
        default=True, validation_alias="GIRAFFE_TRANSLATION_CACHE_ENABLED"
    )

    glossary_path: str = Field(
        default=str(_DEFAULT_GLOSSARY), validation_alias="GIRAFFE_GLOSSARY_PATH"
    )
    require_critical_fields: bool = Field(
        default=True, validation_alias="GIRAFFE_REQUIRE_CRITICAL_FIELDS"
    )
    default_target_language: str = Field(
        default="en", validation_alias="GIRAFFE_DEFAULT_TARGET_LANGUAGE"
    )

    @property
    def resolved_glossary_path(self) -> Path:
        """Return the glossary path, falling back to the bundled default."""
        candidate = Path(self.glossary_path)
        if candidate.exists():
            return candidate
        return _DEFAULT_GLOSSARY


@lru_cache
def get_settings() -> Settings:
    """Return a cached ``Settings`` instance."""
    return Settings()
