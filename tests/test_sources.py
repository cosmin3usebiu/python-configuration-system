"""Tests for source registration, discovery, and raw source loading."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from python_configuration_system import (
    EnvConfigSource,
    FileConfigSource,
    SourceLoadError,
    SourceRegistrationError,
    SourceRegistry,
)


def test_environment_source_discovers_matching_variables(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify environment discovery exposes matching variable names."""
    monkeypatch.setenv("APP_API_KEY", "secret")
    monkeypatch.setenv("APP_TIMEOUT", "30")
    monkeypatch.setenv("OTHER_VALUE", "ignored")

    source = EnvConfigSource(prefix="APP_")
    discovery = source.discover()

    assert discovery.metadata.source_name == "env"
    assert discovery.metadata.kind == "environment"
    assert discovery.locations == ("APP_API_KEY", "APP_TIMEOUT")


def test_environment_source_loads_matching_variables(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify environment loading returns normalized raw keys."""
    monkeypatch.setenv("APP_API_KEY", "secret")
    monkeypatch.setenv("APP_TIMEOUT", "30")
    monkeypatch.setenv("OTHER_VALUE", "ignored")

    source = EnvConfigSource(prefix="APP_")
    payload = source.load()

    assert payload.source_name == "env"
    assert payload.data == {
        "api_key": "secret",
        "timeout": "30",
    }
    assert payload.metadata is not None
    assert payload.metadata.supports_profiles is False


def test_file_source_discovers_configured_path(tmp_path: Path) -> None:
    """Verify file discovery reports the configured path."""
    config_path = tmp_path / "config.json"
    source = FileConfigSource(base_path=config_path)

    discovery = source.discover()

    assert discovery.metadata.source_name == "file"
    assert discovery.metadata.kind == "file"
    assert discovery.locations == (str(config_path),)


def test_file_source_loads_json_mapping(tmp_path: Path) -> None:
    """Verify file loading returns the raw top-level JSON mapping."""
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps({"service_name": "demo", "timeout_seconds": 30}),
        encoding="utf-8",
    )

    source = FileConfigSource(base_path=config_path)
    payload = source.load()

    assert payload.source_name == "file"
    assert payload.data == {
        "service_name": "demo",
        "timeout_seconds": 30,
    }


def test_file_source_rejects_non_mapping_json_payload(tmp_path: Path) -> None:
    """Verify file loading rejects unsupported top-level JSON structures."""
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(["invalid"]), encoding="utf-8")

    source = FileConfigSource(base_path=config_path)

    with pytest.raises(SourceLoadError):
        source.load()


def test_source_registry_registers_sources_by_name() -> None:
    """Verify source registry preserves registration order."""
    registry = SourceRegistry().register(EnvConfigSource()).register(
        FileConfigSource(base_path=Path("config.json"))
    )

    assert registry.source_names == ("env", "file")
    assert registry.get_source("env") is not None
    assert registry.get_source("missing") is None


def test_source_registry_rejects_duplicate_source_names() -> None:
    """Verify source registry rejects duplicate source names."""
    with pytest.raises(SourceRegistrationError):
        SourceRegistry(
            sources=(
                EnvConfigSource(name="shared"),
                FileConfigSource(base_path=Path("config.json"), name="shared"),
            )
        )
