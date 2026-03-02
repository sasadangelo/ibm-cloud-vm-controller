# -----------------------------------------------------------------------------
# Copyright (c) 2026 Salvatore D'Angelo, Code4Projects
# Licensed under the MIT License. See LICENSE.md for details.
# -----------------------------------------------------------------------------
from pathlib import Path
from typing import ClassVar
from pydantic import Field
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict
from pydantic_settings.sources import YamlConfigSettingsSource

# Resolve config.yaml relative to this file (src/config.yaml)
_CONFIG_YAML = Path(__file__).parent.parent / "config.yaml"


class LogConfig(BaseSettings):
    """Logging configuration settings."""

    level: str = Field(default="INFO", description="Log level")
    console: bool = Field(default=True, description="Enable console logging")
    file: str | None = Field(default=None, description="Log file path")
    rotation: str = Field(default="10 MB", description="Log rotation size")
    retention: str = Field(default="7 days", description="Log retention period")
    compression: str = Field(default="zip", description="Log compression format")

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(extra="ignore")


class AppSettings(BaseSettings):
    log: LogConfig

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        yaml_file=str(_CONFIG_YAML),
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Customize settings sources: YAML file only."""
        return (
            YamlConfigSettingsSource(settings_cls),
            env_settings,
            init_settings,
        )


# Load settings at module import
vsi_controller_config: AppSettings = AppSettings()  # type: ignore[call-arg]
