"""Runtime configuration object definitions.

This module defines the immutable runtime object that applications consume
after validation has produced contract-checked configuration data.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from types import MappingProxyType

from python_configuration_system.types import ConfigMapping
from python_configuration_system.types import ConfigValue
from python_configuration_system.types import FieldName
from python_configuration_system.types import ProfileName
from python_configuration_system.types import SourceName
from python_configuration_system.validate import ValidationReport


@dataclass(slots=True, frozen=True)
class ResolvedConfig:
    """Represent immutable runtime configuration for application code.

    Purpose:
        Provide a lightweight runtime-facing view over validated configuration
        values without performing loading, merging, or validation work.

    Parameters:
        schema_name: Name of the originating schema.
        profile_name: Active resolved profile name, if any.
        values: Final validated configuration mapping.
        source_names: Ordered source names that contributed to resolution.
        applied_defaults: Ordered field names that received schema defaults.

    Attributes:
        schema_name: Name of the originating schema.
        profile_name: Active resolved profile name, if any.
        values: Immutable runtime configuration mapping.
        source_names: Ordered source names that contributed to resolution.
        applied_defaults: Ordered field names that received schema defaults.

    Raises:
        AttributeError: When attribute-style access is used for a missing field.
        KeyError: When required mapping access is used for a missing field.

    Usage Notes:
        Attribute-style access is available for field names that do not collide
        with existing object attributes or methods. Mapping access and helper
        methods remain the unambiguous access path for all fields.

    Example:
        >>> from python_configuration_system.validate import ValidationReport
        >>> report = ValidationReport(
        ...     schema_name="service",
        ...     values={"service_name": "demo"},
        ...     source_names=("file",),
        ... )
        >>> config = ResolvedConfig.from_validation_report(validation_report=report)
        >>> config.service_name
        'demo'
    """

    schema_name: str
    profile_name: ProfileName | None
    values: ConfigMapping
    source_names: tuple[SourceName, ...] = field(default_factory=tuple)
    applied_defaults: tuple[FieldName, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        """Freeze runtime data for downstream consumers."""
        object.__setattr__(self, "values", MappingProxyType(dict(self.values)))
        object.__setattr__(self, "source_names", tuple(self.source_names))
        object.__setattr__(self, "applied_defaults", tuple(self.applied_defaults))

    @classmethod
    def from_validation_report(
        cls,
        *,
        validation_report: ValidationReport,
        profile_name: ProfileName | None = None,
    ) -> "ResolvedConfig":
        """Create a runtime configuration object from validated data.

        Purpose:
            Convert immutable validation output into the runtime view consumed
            by application code.

        Parameters:
            validation_report: Immutable validation output.
            profile_name: Optional resolved profile name.

        Returns:
            Immutable runtime configuration object.

        Raises:
            No additional exceptions are raised after successful construction.

        Usage Notes:
            This constructor does not inspect validation issues. Policy for
            whether a report is acceptable belongs to the orchestration layer.

        Example:
            >>> report = ValidationReport(
            ...     schema_name="service",
            ...     values={"service_name": "demo"},
            ...     source_names=("file",),
            ... )
            >>> config = ResolvedConfig.from_validation_report(
            ...     validation_report=report,
            ...     profile_name="dev",
            ... )
            >>> config.profile_name
            'dev'
        """
        return cls(
            schema_name=validation_report.schema_name,
            profile_name=profile_name,
            values=validation_report.values,
            source_names=validation_report.source_names,
            applied_defaults=validation_report.applied_defaults,
        )

    def __getitem__(self, field_name: FieldName) -> ConfigValue:
        """Return a configuration value by field name."""
        return self.values[field_name]

    def __iter__(self) -> Iterator[FieldName]:
        """Iterate over configured field names."""
        return iter(self.values)

    def __len__(self) -> int:
        """Return the number of resolved configuration fields."""
        return len(self.values)

    def __contains__(self, field_name: object) -> bool:
        """Return whether a field exists in the runtime mapping."""
        return field_name in self.values

    def __getattr__(self, attribute_name: str) -> ConfigValue:
        """Expose configuration values through attribute-style access."""
        try:
            return self.values[attribute_name]
        except KeyError as exc:
            raise AttributeError(
                f"Resolved configuration has no field '{attribute_name}'."
            ) from exc

    def get(
        self,
        field_name: FieldName,
        default: ConfigValue | None = None,
    ) -> ConfigValue:
        """Return a configuration value or a fallback default.

        Purpose:
            Provide safe retrieval when a caller wants optional access without
            raising ``KeyError``.

        Parameters:
            field_name: Field to retrieve.
            default: Fallback value returned when the field is absent.

        Returns:
            Resolved configuration value when present, otherwise ``default``.

        Raises:
            No additional exceptions are raised during normal retrieval.

        Usage Notes:
            This method is the preferred optional access path when attribute
            access would be ambiguous or when absence is acceptable.
        """
        return self.values.get(field_name, default)

    def require(self, field_name: FieldName) -> ConfigValue:
        """Return a configuration value and fail if it is absent.

        Purpose:
            Provide explicit required retrieval with a stable error message for
            application code that expects a field to be present.

        Parameters:
            field_name: Field that must exist.

        Returns:
            Resolved configuration value for the requested field.

        Raises:
            KeyError: If the requested field is absent from the runtime object.

        Usage Notes:
            Prefer this method when absence indicates a programming error or an
            upstream orchestration problem.
        """
        if field_name not in self.values:
            raise KeyError(
                f"Resolved configuration field '{field_name}' is not available."
            )
        return self.values[field_name]
