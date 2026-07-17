"""Tests for diagnostics summaries over validation and runtime objects."""

from __future__ import annotations

from types import MappingProxyType

from python_configuration_system.diagnostics import ConfigurationSummary
from python_configuration_system.diagnostics import DiagnosticsFormatter
from python_configuration_system.diagnostics import DiagnosticsMode
from python_configuration_system.runtime import ResolvedConfig
from python_configuration_system.validate import ValidationIssue
from python_configuration_system.validate import ValidationReport
from python_configuration_system.validate import ValidationSeverity


def build_validation_report() -> ValidationReport:
    """Create a validation report for diagnostics-focused tests."""
    return ValidationReport(
        schema_name="service",
        values={
            "service_name": "demo",
            "timeout_seconds": 30,
            "api_token": "token-value",
        },
        source_names=("file", "env"),
        issues=(
            ValidationIssue(
                field_name="extra_flag",
                code="unknown_field",
                message="Unknown field 'extra_flag' is not defined by the schema.",
            ),
            ValidationIssue(
                field_name="api_token",
                code="type_mismatch",
                message="Field 'api_token' expects value type 'str'.",
                severity=ValidationSeverity.WARNING,
                secret=True,
            ),
        ),
        applied_defaults=("timeout_seconds",),
        field_origins={
            "service_name": "file",
            "timeout_seconds": "schema_default",
            "api_token": "env",
        },
        secret_fields=("api_token",),
    )


def build_resolved_config() -> ResolvedConfig:
    """Create a runtime configuration object for diagnostics-focused tests."""
    return ResolvedConfig.from_validation_report(
        validation_report=build_validation_report(),
        profile_name="dev",
    )


def test_quiet_diagnostics_summary_contains_startup_metadata() -> None:
    """Verify quiet diagnostics include only compact startup information."""
    summary = DiagnosticsFormatter().summarize(
        validation_report=build_validation_report(),
        resolved_config=build_resolved_config(),
        mode=DiagnosticsMode.QUIET,
    )

    assert isinstance(summary, ConfigurationSummary)
    assert summary.mode is DiagnosticsMode.QUIET
    assert summary.lines == (
        "Schema: service",
        "Profile: dev",
        "Loaded fields: 3",
        "Sources: file, env",
    )


def test_verbose_diagnostics_include_field_origins_defaults_and_statistics() -> None:
    """Verify verbose diagnostics include structural metadata sections."""
    summary = DiagnosticsFormatter().summarize(
        validation_report=build_validation_report(),
        resolved_config=build_resolved_config(),
        mode=DiagnosticsMode.VERBOSE,
    )

    assert summary.mode is DiagnosticsMode.VERBOSE
    assert "Field origins:" in summary.lines
    assert "  service_name: file" in summary.lines
    assert "Applied defaults:" in summary.lines
    assert "  timeout_seconds" in summary.lines
    assert "Validation statistics:" in summary.lines
    assert "  issues=2, errors=1, warnings=1" in summary.lines
    assert "Runtime metadata:" in summary.lines


def test_verbose_diagnostics_redact_secret_values() -> None:
    """Verify verbose diagnostics never expose secret runtime values."""
    summary = DiagnosticsFormatter().summarize(
        validation_report=build_validation_report(),
        resolved_config=build_resolved_config(),
        mode=DiagnosticsMode.VERBOSE,
    )

    assert summary.secret_fields["api_token"] == "[REDACTED]"
    assert "  api_token: [REDACTED]" in summary.lines
    joined_lines = "\n".join(summary.lines)
    assert "token-value" not in joined_lines


def test_configuration_summary_is_immutable() -> None:
    """Verify diagnostics summaries are immutable boundary objects."""
    summary = DiagnosticsFormatter().summarize(
        validation_report=build_validation_report(),
        resolved_config=build_resolved_config(),
        mode=DiagnosticsMode.VERBOSE,
    )

    assert isinstance(summary.field_origins, MappingProxyType)
    assert isinstance(summary.secret_fields, MappingProxyType)
    assert isinstance(summary.runtime_metadata, MappingProxyType)
