"""Tests for runtime configuration access over validated data."""

from __future__ import annotations

from types import MappingProxyType

import pytest

from python_configuration_system.runtime import ResolvedConfig
from python_configuration_system.validate import ValidationReport


def build_validation_report() -> ValidationReport:
    """Create a validation report for runtime-focused tests."""
    return ValidationReport(
        schema_name="service",
        values={
            "service_name": "demo",
            "timeout_seconds": 30,
        },
        source_names=("file", "env"),
        applied_defaults=("timeout_seconds",),
    )


def test_runtime_can_be_created_from_validation_report() -> None:
    """Verify runtime configuration preserves validation metadata."""
    config = ResolvedConfig.from_validation_report(
        validation_report=build_validation_report(),
        profile_name="dev",
    )

    assert config.schema_name == "service"
    assert config.profile_name == "dev"
    assert config.source_names == ("file", "env")
    assert config.applied_defaults == ("timeout_seconds",)


def test_runtime_supports_mapping_and_attribute_access() -> None:
    """Verify runtime values are available through multiple access styles."""
    config = ResolvedConfig.from_validation_report(
        validation_report=build_validation_report(),
    )

    assert config["service_name"] == "demo"
    assert config.service_name == "demo"
    assert config.get("service_name") == "demo"
    assert config.require("service_name") == "demo"
    assert "service_name" in config


def test_runtime_supports_iteration_and_length() -> None:
    """Verify runtime objects behave like lightweight immutable mappings."""
    config = ResolvedConfig.from_validation_report(
        validation_report=build_validation_report(),
    )

    assert tuple(iter(config)) == ("service_name", "timeout_seconds")
    assert len(config) == 2


def test_runtime_get_returns_default_for_missing_field() -> None:
    """Verify optional retrieval can return a fallback default."""
    config = ResolvedConfig.from_validation_report(
        validation_report=build_validation_report(),
    )

    assert config.get("missing_field", "fallback") == "fallback"


def test_runtime_require_raises_for_missing_field() -> None:
    """Verify required retrieval rejects absent fields."""
    config = ResolvedConfig.from_validation_report(
        validation_report=build_validation_report(),
    )

    with pytest.raises(KeyError):
        config.require("missing_field")


def test_runtime_attribute_access_raises_attribute_error_for_missing_field() -> None:
    """Verify missing attribute-style access raises ``AttributeError``."""
    config = ResolvedConfig.from_validation_report(
        validation_report=build_validation_report(),
    )

    with pytest.raises(AttributeError):
        _ = config.missing_field


def test_runtime_is_immutable() -> None:
    """Verify runtime data crossing the boundary remains immutable."""
    config = ResolvedConfig.from_validation_report(
        validation_report=build_validation_report(),
    )

    assert isinstance(config.values, MappingProxyType)

    with pytest.raises(TypeError):
        config.values["service_name"] = "prod"  # type: ignore[index]
