"""Diagnostics and redacted configuration inspection helpers.

This module defines the diagnostics presentation layer used to summarize
validated runtime configuration state without exposing secrets.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType
from typing import Mapping

from python_configuration_system.runtime import ResolvedConfig
from python_configuration_system.types import FieldName, SourceName
from python_configuration_system.validate import ValidationReport, ValidationSeverity


class DiagnosticsMode(StrEnum):
    """Represent supported diagnostics output modes.

    Purpose:
        Distinguish compact startup summaries from verbose engineering
        inspection output without changing the diagnostics data model.

    Parameters:
        Enumeration members do not define constructor parameters.

    Attributes:
        QUIET: Compact startup summary.
        VERBOSE: Detailed startup summary with structural metadata.

    Raises:
        No additional exceptions are raised by the enumeration itself.

    Usage Notes:
        Diagnostics mode influences presentation only. It does not alter
        loading, validation, or runtime behavior.

    Example:
        >>> DiagnosticsMode.QUIET.value
        'quiet'
    """

    QUIET = "quiet"
    VERBOSE = "verbose"


@dataclass(slots=True, frozen=True)
class ValidationStatistics:
    """Describe validation statistics for diagnostics output.

    Purpose:
        Provide a compact validation summary for diagnostics without exposing
        the full issue collection during ordinary startup output.

    Parameters:
        total_issues: Total number of validation issues.
        error_count: Number of error-severity issues.
        warning_count: Number of warning-severity issues.

    Attributes:
        total_issues: Total number of validation issues.
        error_count: Number of error-severity issues.
        warning_count: Number of warning-severity issues.

    Raises:
        No additional exceptions are raised after successful construction.

    Usage Notes:
        Statistics are descriptive only. They do not determine whether a
        configuration is accepted.

    Example:
        >>> ValidationStatistics(total_issues=1, error_count=1).error_count
        1
    """

    total_issues: int
    error_count: int
    warning_count: int = 0


@dataclass(slots=True, frozen=True)
class ConfigurationSummary:
    """Describe a redacted configuration summary for diagnostics.

    Purpose:
        Carry a structured, presentation-ready startup summary without
        mutating runtime or validation objects.

    Parameters:
        mode: Diagnostics presentation mode.
        schema_name: Name of the originating schema.
        profile_name: Active resolved profile name, if any.
        loaded_field_count: Number of fields available at runtime.
        source_names: Ordered source list.
        field_origins: Immutable field-to-source mapping.
        applied_defaults: Ordered applied default field names.
        secret_fields: Immutable redacted secret mapping.
        validation_statistics: Aggregate validation statistics.
        runtime_metadata: Immutable runtime metadata summary.
        lines: Presentation-ready summary lines.

    Attributes:
        mode: Diagnostics presentation mode.
        schema_name: Name of the originating schema.
        profile_name: Active resolved profile name, if any.
        loaded_field_count: Number of fields available at runtime.
        source_names: Ordered source list.
        field_origins: Immutable field-to-source mapping.
        applied_defaults: Ordered applied default field names.
        secret_fields: Immutable redacted secret mapping.
        validation_statistics: Aggregate validation statistics.
        runtime_metadata: Immutable runtime metadata summary.
        lines: Presentation-ready summary lines.

    Raises:
        No additional exceptions are raised after successful construction.

    Usage Notes:
        Summary lines never include raw secret values or environment contents.

    Example:
        >>> summary = ConfigurationSummary(
        ...     mode=DiagnosticsMode.QUIET,
        ...     schema_name="service",
        ...     profile_name=None,
        ...     loaded_field_count=1,
        ...     source_names=("file",),
        ...     field_origins={},
        ...     applied_defaults=(),
        ...     secret_fields={},
        ...     validation_statistics=ValidationStatistics(
        ...         total_issues=0,
        ...         error_count=0,
        ...     ),
        ...     runtime_metadata={"loaded_field_count": "1"},
        ...     lines=("Schema: service",),
        ... )
        >>> summary.lines[0]
        'Schema: service'
    """

    mode: DiagnosticsMode
    schema_name: str
    profile_name: str | None
    loaded_field_count: int
    source_names: tuple[SourceName, ...] = ()
    field_origins: Mapping[FieldName, SourceName] = field(default_factory=dict)
    applied_defaults: tuple[FieldName, ...] = ()
    secret_fields: Mapping[FieldName, str] = field(default_factory=dict)
    validation_statistics: ValidationStatistics = field(
        default_factory=lambda: ValidationStatistics(total_issues=0, error_count=0)
    )
    runtime_metadata: Mapping[str, str] = field(default_factory=dict)
    lines: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        """Freeze diagnostics summary data for downstream consumers."""
        object.__setattr__(self, "source_names", tuple(self.source_names))
        object.__setattr__(
            self,
            "field_origins",
            MappingProxyType(dict(self.field_origins)),
        )
        object.__setattr__(self, "applied_defaults", tuple(self.applied_defaults))
        object.__setattr__(
            self,
            "secret_fields",
            MappingProxyType(dict(self.secret_fields)),
        )
        object.__setattr__(
            self,
            "runtime_metadata",
            MappingProxyType(dict(self.runtime_metadata)),
        )
        object.__setattr__(self, "lines", tuple(self.lines))


@dataclass(slots=True)
class DiagnosticsFormatter:
    """Format diagnostics for validated runtime configuration state.

    Purpose:
        Generate quiet and verbose startup summaries from immutable validation
        and runtime objects without performing loading, merging, or validation.

    Parameters:
        redaction_token: Placeholder text used for secret values.

    Attributes:
        redaction_token: Placeholder text used for secret values.

    Raises:
        No additional exceptions are raised during normal formatting.

    Usage Notes:
        Diagnostics formatting is a presentation concern only. It must never
        mutate runtime objects or expose raw secret values.

    Example:
        >>> formatter = DiagnosticsFormatter()
        >>> formatter.redaction_token
        '[REDACTED]'
    """

    redaction_token: str = "[REDACTED]"

    def summarize(
        self,
        *,
        validation_report: ValidationReport,
        resolved_config: ResolvedConfig,
        mode: DiagnosticsMode = DiagnosticsMode.QUIET,
    ) -> ConfigurationSummary:
        """Produce a redacted summary of resolved configuration data.

        Args:
            validation_report: Immutable validation output.
            resolved_config: Immutable runtime configuration object.
            mode: Requested diagnostics mode.

        Returns:
            Structured diagnostics summary for startup output.
        """
        validation_statistics = self._build_validation_statistics(validation_report)
        secret_fields = self._build_secret_field_summary(
            validation_report=validation_report,
            resolved_config=resolved_config,
        )
        runtime_metadata = self._build_runtime_metadata(
            resolved_config=resolved_config,
            validation_report=validation_report,
        )
        lines = self._build_lines(
            validation_report=validation_report,
            resolved_config=resolved_config,
            validation_statistics=validation_statistics,
            secret_fields=secret_fields,
            runtime_metadata=runtime_metadata,
            mode=mode,
        )

        return ConfigurationSummary(
            mode=mode,
            schema_name=resolved_config.schema_name,
            profile_name=resolved_config.profile_name,
            loaded_field_count=len(resolved_config),
            source_names=resolved_config.source_names,
            field_origins=validation_report.field_origins,
            applied_defaults=resolved_config.applied_defaults,
            secret_fields=secret_fields,
            validation_statistics=validation_statistics,
            runtime_metadata=runtime_metadata,
            lines=lines,
        )

    def _build_validation_statistics(
        self,
        validation_report: ValidationReport,
    ) -> ValidationStatistics:
        """Build aggregate validation statistics for diagnostics."""
        error_count = sum(
            1
            for issue in validation_report.issues
            if issue.severity is ValidationSeverity.ERROR
        )
        warning_count = sum(
            1
            for issue in validation_report.issues
            if issue.severity is ValidationSeverity.WARNING
        )
        return ValidationStatistics(
            total_issues=len(validation_report.issues),
            error_count=error_count,
            warning_count=warning_count,
        )

    def _build_secret_field_summary(
        self,
        *,
        validation_report: ValidationReport,
        resolved_config: ResolvedConfig,
    ) -> Mapping[FieldName, str]:
        """Build the redacted secret field summary."""
        return {
            field_name: self.redaction_token
            for field_name in validation_report.secret_fields
            if field_name in resolved_config
        }

    def _build_runtime_metadata(
        self,
        *,
        resolved_config: ResolvedConfig,
        validation_report: ValidationReport,
    ) -> Mapping[str, str]:
        """Build runtime metadata for diagnostics output."""
        return {
            "schema": resolved_config.schema_name,
            "profile": resolved_config.profile_name or "none",
            "loaded_field_count": str(len(resolved_config)),
            "source_count": str(len(resolved_config.source_names)),
            "applied_default_count": str(len(resolved_config.applied_defaults)),
            "validation_issue_count": str(len(validation_report.issues)),
        }

    def _build_lines(
        self,
        *,
        validation_report: ValidationReport,
        resolved_config: ResolvedConfig,
        validation_statistics: ValidationStatistics,
        secret_fields: Mapping[FieldName, str],
        runtime_metadata: Mapping[str, str],
        mode: DiagnosticsMode,
    ) -> tuple[str, ...]:
        """Build the presentation-ready diagnostics lines."""
        lines = [
            f"Schema: {resolved_config.schema_name}",
            f"Profile: {resolved_config.profile_name or 'none'}",
            f"Loaded fields: {len(resolved_config)}",
            f"Sources: {', '.join(resolved_config.source_names) or 'none'}",
        ]

        if mode is DiagnosticsMode.VERBOSE:
            lines.extend(
                [
                    "Field origins:",
                    *self._format_field_origins(validation_report),
                    "Applied defaults:",
                    *self._format_applied_defaults(resolved_config),
                    "Validation statistics:",
                    f"  issues={validation_statistics.total_issues}, "
                    f"errors={validation_statistics.error_count}, "
                    f"warnings={validation_statistics.warning_count}",
                    "Configuration sources:",
                    f"  {', '.join(resolved_config.source_names) or 'none'}",
                    "Redacted secrets:",
                    *self._format_secret_fields(secret_fields),
                    "Runtime metadata:",
                    *self._format_runtime_metadata(runtime_metadata),
                ]
            )

        return tuple(lines)

    def _format_field_origins(
        self,
        validation_report: ValidationReport,
    ) -> tuple[str, ...]:
        """Format field origin lines for verbose diagnostics."""
        if not validation_report.field_origins:
            return ("  none",)

        return tuple(
            f"  {field_name}: {source_name}"
            for field_name, source_name in validation_report.field_origins.items()
        )

    def _format_applied_defaults(
        self,
        resolved_config: ResolvedConfig,
    ) -> tuple[str, ...]:
        """Format applied defaults for verbose diagnostics."""
        if not resolved_config.applied_defaults:
            return ("  none",)

        return tuple(
            f"  {field_name}" for field_name in resolved_config.applied_defaults
        )

    def _format_secret_fields(
        self,
        secret_fields: Mapping[FieldName, str],
    ) -> tuple[str, ...]:
        """Format redacted secret field lines for verbose diagnostics."""
        if not secret_fields:
            return ("  none",)

        return tuple(
            f"  {field_name}: {redacted_value}"
            for field_name, redacted_value in secret_fields.items()
        )

    def _format_runtime_metadata(
        self,
        runtime_metadata: Mapping[str, str],
    ) -> tuple[str, ...]:
        """Format runtime metadata lines for verbose diagnostics."""
        return tuple(f"  {key}: {value}" for key, value in runtime_metadata.items())
