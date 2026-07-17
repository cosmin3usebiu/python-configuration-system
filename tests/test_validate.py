"""Tests for schema validation against merged configuration data."""

from __future__ import annotations

from pathlib import Path
from types import MappingProxyType

from python_configuration_system.fields import IntegerField
from python_configuration_system.fields import PathField
from python_configuration_system.fields import SecretField
from python_configuration_system.fields import StringField
from python_configuration_system.merge import MergeDiagnostics
from python_configuration_system.merge import MergeResult
from python_configuration_system.schema import ConfigSchema
from python_configuration_system.validate import ConfigValidator
from python_configuration_system.validate import ValidationSeverity


def build_merge_result(values: dict[str, object]) -> MergeResult:
    """Create a merge result for validation-focused tests."""
    return MergeResult(
        values=values,
        source_names=("file", "env"),
        diagnostics=MergeDiagnostics(
            source_names=("file", "env"),
            field_origins={field_name: "env" for field_name in values},
        ),
    )


def test_validation_applies_defaults_and_preserves_valid_values() -> None:
    """Verify validation applies schema defaults into the validated mapping."""
    schema = ConfigSchema(
        name="service",
        fields=[
            StringField(name="service_name", description="Service name."),
            IntegerField(
                name="timeout_seconds",
                description="Timeout in seconds.",
                required=False,
                default=30,
            ),
        ],
    )

    report = ConfigValidator().validate(
        schema=schema,
        merge_result=build_merge_result({"service_name": "demo"}),
    )

    assert report.schema_name == "service"
    assert report.values["service_name"] == "demo"
    assert report.values["timeout_seconds"] == 30
    assert report.applied_defaults == ("timeout_seconds",)
    assert report.field_origins["service_name"] == "env"
    assert report.field_origins["timeout_seconds"] == "schema_default"
    assert report.issues == ()


def test_validation_reports_missing_required_fields() -> None:
    """Verify missing required schema fields are reported as errors."""
    schema = ConfigSchema(
        name="service",
        fields=[StringField(name="service_name", description="Service name.")],
    )

    report = ConfigValidator().validate(
        schema=schema,
        merge_result=build_merge_result({}),
    )

    assert len(report.issues) == 1
    issue = report.issues[0]
    assert issue.field_name == "service_name"
    assert issue.code == "required_field_missing"
    assert issue.severity is ValidationSeverity.ERROR


def test_validation_reports_unknown_fields_and_filters_them_from_output() -> None:
    """Verify unknown merged fields are reported and omitted from validated data."""
    schema = ConfigSchema(
        name="service",
        fields=[StringField(name="service_name", description="Service name.")],
    )

    report = ConfigValidator().validate(
        schema=schema,
        merge_result=build_merge_result(
            {
                "service_name": "demo",
                "extra_flag": "enabled",
            }
        ),
    )

    assert "service_name" in report.values
    assert "extra_flag" not in report.values
    assert len(report.issues) == 1
    assert report.issues[0].code == "unknown_field"


def test_validation_reports_type_mismatch_without_exposing_secret_values() -> None:
    """Verify secret field issues do not embed sensitive values."""
    schema = ConfigSchema(
        name="service",
        fields=[
            SecretField(
                name="api_token",
                description="Service API token.",
            )
        ],
    )

    report = ConfigValidator().validate(
        schema=schema,
        merge_result=build_merge_result({"api_token": 123}),
    )

    assert len(report.issues) == 1
    issue = report.issues[0]
    assert issue.code == "type_mismatch"
    assert issue.secret is True
    assert report.secret_fields == ("api_token",)
    assert "123" not in issue.message


def test_validation_accepts_path_fields_from_string_values() -> None:
    """Verify path fields accept raw string path values at validation time."""
    schema = ConfigSchema(
        name="service",
        fields=[
            PathField(
                name="workspace_root",
                description="Workspace root path.",
                required=False,
            )
        ],
    )

    report = ConfigValidator().validate(
        schema=schema,
        merge_result=build_merge_result({"workspace_root": "data/workspace"}),
    )

    assert report.issues == ()
    assert report.values["workspace_root"] == "data/workspace"


def test_validation_accepts_path_object_for_path_field() -> None:
    """Verify path fields accept ``Path`` instances as compatible values."""
    schema = ConfigSchema(
        name="service",
        fields=[
            PathField(
                name="workspace_root",
                description="Workspace root path.",
                required=False,
            )
        ],
    )

    report = ConfigValidator().validate(
        schema=schema,
        merge_result=build_merge_result({"workspace_root": Path("workspace")}),
    )

    assert report.issues == ()


def test_validation_report_is_immutable() -> None:
    """Verify validation output is immutable for downstream consumers."""
    schema = ConfigSchema(
        name="service",
        fields=[StringField(name="service_name", description="Service name.")],
    )

    report = ConfigValidator().validate(
        schema=schema,
        merge_result=build_merge_result({"service_name": "demo"}),
    )

    assert isinstance(report.values, MappingProxyType)
    assert isinstance(report.field_origins, MappingProxyType)
