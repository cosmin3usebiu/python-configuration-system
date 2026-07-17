"""Validation routines for merged configuration data.

This module defines the validation engine used to check merged configuration
values against a declarative schema and produce immutable validation output.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from types import MappingProxyType

from python_configuration_system.fields import ConfigField
from python_configuration_system.fields import PathField
from python_configuration_system.fields import UNSET
from python_configuration_system.merge import MergeResult
from python_configuration_system.schema import ConfigSchema
from python_configuration_system.types import ConfigMapping
from python_configuration_system.types import ConfigValue
from python_configuration_system.types import FieldName
from python_configuration_system.types import SourceName


class ValidationSeverity(StrEnum):
    """Represent validation issue severity levels.

    Purpose:
        Classify validation findings without coupling the validator to any
        diagnostics formatting or exception policy.

    Parameters:
        Enumeration members do not define constructor parameters.

    Attributes:
        ERROR: Validation finding that indicates contract failure.
        WARNING: Validation finding that does not necessarily block use.

    Raises:
        No additional exceptions are raised by the enumeration itself.

    Usage Notes:
        Severity values are descriptive only. They do not automatically raise
        exceptions or alter validation flow.

    Example:
        >>> ValidationSeverity.ERROR.value
        'error'
    """

    ERROR = "error"
    WARNING = "warning"


@dataclass(slots=True, frozen=True)
class ValidationIssue:
    """Describe a single validation issue.

    Purpose:
        Capture one schema-contract violation or validation finding without
        exposing runtime formatting concerns.

    Parameters:
        field_name: Field associated with the issue.
        code: Stable machine-readable validation code.
        message: Human-readable validation message.
        severity: Severity classification for the issue.
        secret: Whether the issue relates to a secret field.

    Attributes:
        field_name: Field associated with the issue.
        code: Stable machine-readable validation code.
        message: Human-readable validation message.
        severity: Severity classification for the issue.
        secret: Whether the issue relates to a secret field.

    Raises:
        No additional exceptions are raised after successful construction.

    Usage Notes:
        Issue messages intentionally avoid embedding sensitive values.

    Example:
        >>> issue = ValidationIssue(
        ...     field_name="service_name",
        ...     code="required_field_missing",
        ...     message="Required field 'service_name' is missing.",
        ... )
        >>> issue.code
        'required_field_missing'
    """

    field_name: FieldName
    code: str
    message: str
    severity: ValidationSeverity = ValidationSeverity.ERROR
    secret: bool = False


@dataclass(slots=True, frozen=True)
class ValidationReport:
    """Describe the aggregate result of a validation pass.

    Purpose:
        Expose the validated configuration mapping, source metadata, and
        validation findings as immutable output for later layers.

    Parameters:
        schema_name: Name of the schema used for validation.
        values: Validated configuration mapping with defaults applied.
        source_names: Ordered merge source names associated with the input.
        issues: Ordered validation findings.
        applied_defaults: Ordered field names that received schema defaults.
        field_origins: Final source associated with each validated field.
        secret_fields: Ordered field names that should be redacted in
            diagnostics.

    Attributes:
        schema_name: Name of the schema used for validation.
        values: Immutable validated configuration mapping.
        source_names: Ordered merge source names associated with the input.
        issues: Ordered validation findings.
        applied_defaults: Ordered field names that received schema defaults.
        field_origins: Immutable mapping of fields to their final source names.
        secret_fields: Ordered field names that should be redacted.

    Raises:
        No additional exceptions are raised after successful construction.

    Usage Notes:
        Validation reports remain pure data objects. They do not raise
        exceptions, format diagnostics, or create runtime configuration.

    Example:
        >>> report = ValidationReport(
        ...     schema_name="service",
        ...     values={"service_name": "demo"},
        ...     source_names=("file",),
        ...     field_origins={"service_name": "file"},
        ... )
        >>> report.values["service_name"]
        'demo'
    """

    schema_name: str
    values: ConfigMapping
    source_names: tuple[SourceName, ...] = ()
    issues: tuple[ValidationIssue, ...] = field(default_factory=tuple)
    applied_defaults: tuple[FieldName, ...] = ()
    field_origins: Mapping[FieldName, SourceName] = field(default_factory=dict)
    secret_fields: tuple[FieldName, ...] = ()

    def __post_init__(self) -> None:
        """Freeze validation output for downstream consumers."""
        object.__setattr__(self, "values", MappingProxyType(dict(self.values)))
        object.__setattr__(self, "source_names", tuple(self.source_names))
        object.__setattr__(self, "issues", tuple(self.issues))
        object.__setattr__(self, "applied_defaults", tuple(self.applied_defaults))
        object.__setattr__(
            self,
            "field_origins",
            MappingProxyType(dict(self.field_origins)),
        )
        object.__setattr__(self, "secret_fields", tuple(self.secret_fields))


@dataclass(slots=True)
class ConfigValidator:
    """Validate merged configuration data against a schema contract.

    Purpose:
        Apply schema-driven validation rules to merged configuration data while
        remaining independent from runtime configuration and diagnostics
        formatting.

    Parameters:
        This validator does not define constructor parameters.

    Attributes:
        No additional public attributes are defined.

    Raises:
        This validator reports validation issues in a ``ValidationReport``
        rather than raising exceptions during normal validation.

    Usage Notes:
        Validation applies schema defaults, filters unknown fields from the
        validated output, and records contract violations as issues.

    Example:
        >>> from python_configuration_system.fields import StringField
        >>> from python_configuration_system.merge import MergeDiagnostics
        >>> from python_configuration_system.merge import MergeResult
        >>> schema = ConfigSchema(
        ...     name="service",
        ...     fields=[StringField(name="service_name", description="Name.")],
        ... )
        >>> merge_result = MergeResult(
        ...     values={"service_name": "demo"},
        ...     source_names=("file",),
        ...     diagnostics=MergeDiagnostics(
        ...         source_names=("file",),
        ...         field_origins={"service_name": "file"},
        ...     ),
        ... )
        >>> report = ConfigValidator().validate(schema=schema, merge_result=merge_result)
        >>> report.values["service_name"]
        'demo'
    """

    def validate(
        self,
        *,
        schema: ConfigSchema,
        merge_result: MergeResult,
    ) -> ValidationReport:
        """Validate merged configuration data against a schema.

        Args:
            schema: Schema that defines the configuration contract.
            merge_result: Merged configuration data to validate.

        Returns:
            Immutable validation output containing values and issues.
        """
        validated_values: dict[FieldName, ConfigValue] = {}
        issues: list[ValidationIssue] = []
        applied_defaults: list[FieldName] = []
        field_origins: dict[FieldName, SourceName] = {}
        secret_fields = tuple(
            field_name
            for field_name, config_field in schema.fields.items()
            if config_field.secret
        )

        for field_name in merge_result.values:
            if field_name not in schema.fields:
                issues.append(
                    ValidationIssue(
                        field_name=field_name,
                        code="unknown_field",
                        message=f"Unknown field '{field_name}' is not defined by the schema.",
                    )
                )

        for field_name, config_field in schema.fields.items():
            if field_name in merge_result.values:
                field_value = merge_result.values[field_name]
                field_origins[field_name] = merge_result.diagnostics.field_origins.get(
                    field_name,
                    "unknown",
                )
            elif config_field.has_default:
                field_value = config_field.default
                applied_defaults.append(field_name)
                field_origins[field_name] = "schema_default"
            else:
                field_value = UNSET

            if field_value is UNSET:
                if config_field.required:
                    issues.append(
                        ValidationIssue(
                            field_name=field_name,
                            code="required_field_missing",
                            message=f"Required field '{field_name}' is missing.",
                            secret=config_field.secret,
                        )
                    )
                continue

            validated_values[field_name] = field_value
            field_issues = self._validate_field_value(
                config_field=config_field,
                field_value=field_value,
            )
            issues.extend(field_issues)

        return ValidationReport(
            schema_name=schema.name,
            values=validated_values,
            source_names=merge_result.source_names,
            issues=tuple(issues),
            applied_defaults=tuple(applied_defaults),
            field_origins=field_origins,
            secret_fields=secret_fields,
        )

    def _validate_field_value(
        self,
        *,
        config_field: ConfigField,
        field_value: ConfigValue,
    ) -> tuple[ValidationIssue, ...]:
        """Validate a single field value against its schema definition."""
        if field_value is None:
            if config_field.allow_none:
                return ()
            return (
                ValidationIssue(
                    field_name=config_field.name,
                    code="none_not_allowed",
                    message=(
                        f"Field '{config_field.name}' does not allow a null value."
                    ),
                    secret=config_field.secret,
                ),
            )

        if self._is_type_compatible(config_field=config_field, field_value=field_value):
            return ()

        return (
            ValidationIssue(
                field_name=config_field.name,
                code="type_mismatch",
                message=(
                    f"Field '{config_field.name}' expects value type "
                    f"'{self._describe_expected_type(config_field)}'."
                ),
                secret=config_field.secret,
            ),
        )

    def _is_type_compatible(
        self,
        *,
        config_field: ConfigField,
        field_value: ConfigValue,
    ) -> bool:
        """Return whether a field value is compatible with its schema type."""
        if isinstance(config_field, PathField):
            return isinstance(field_value, (str, Path))

        expected_type = config_field.value_type

        if expected_type is object:
            return True

        if expected_type is int:
            return isinstance(field_value, int) and not isinstance(field_value, bool)

        if expected_type is float:
            return isinstance(field_value, float)

        if expected_type is bool:
            return isinstance(field_value, bool)

        if expected_type is dict:
            return isinstance(field_value, Mapping)

        if expected_type is list:
            return isinstance(field_value, list)

        return isinstance(field_value, expected_type)

    def _describe_expected_type(self, config_field: ConfigField) -> str:
        """Return a human-readable expected type description."""
        if isinstance(config_field, PathField):
            return "str | Path"

        expected_type = config_field.value_type
        if isinstance(expected_type, tuple):
            return " | ".join(type_item.__name__ for type_item in expected_type)
        return expected_type.__name__
