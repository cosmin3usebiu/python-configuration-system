"""Field definitions for configuration schema objects.

This module defines the public declarative field model used by schemas. Field
classes intentionally describe configuration shape only during Milestone 3.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping

from python_configuration_system.errors import SchemaDefinitionError
from python_configuration_system.paths import PathRules
from python_configuration_system.types import ConfigValue
from python_configuration_system.types import FieldName
from python_configuration_system.types import FieldRuntimeType


class UnsetDefault:
    """Represent the absence of a configured default value."""

    def __repr__(self) -> str:
        """Return a stable debug representation for the sentinel."""
        return "UNSET"


UNSET = UnsetDefault()


@dataclass(slots=True, frozen=True, kw_only=True)
class ConfigField:
    """Describe a single configuration field.

    Attributes:
        name: Public field identifier used by schemas and diagnostics.
        description: Human-readable explanation of the field's purpose.
        value_type: Declared Python runtime type for resolved values.
        required: Whether a value must be supplied by a later source.
        default: Default value used when no higher-precedence value is present.
        allow_none: Whether ``None`` is a valid resolved value.
        secret: Whether the field should be redacted in future diagnostics.
        environment_variable: Optional explicit environment variable name.
        metadata: Reserved extension point for future field annotations.

    Raises:
        SchemaDefinitionError: If the field declaration is structurally invalid.

    Usage Notes:
        Field instances are declarative only in this milestone. Loading,
        coercion, and validation behavior will be added later.
    """

    name: FieldName
    description: str
    value_type: FieldRuntimeType = object
    required: bool = True
    default: ConfigValue | UnsetDefault = UNSET
    allow_none: bool = False
    secret: bool = False
    environment_variable: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Normalize and validate the declarative field definition."""
        normalized_name = self.name.strip()
        normalized_description = self.description.strip()

        if not normalized_name:
            raise SchemaDefinitionError("Configuration field names must be non-empty.")

        if not normalized_description:
            raise SchemaDefinitionError(
                f"Configuration field '{self.name}' must include a description."
            )

        if self.required and self.has_default:
            raise SchemaDefinitionError(
                f"Configuration field '{self.name}' cannot be required and define a default."
            )

        if self.default is None and not self.allow_none:
            raise SchemaDefinitionError(
                f"Configuration field '{self.name}' uses a None default but allow_none is False."
            )

        if self.environment_variable is not None:
            normalized_environment_variable = self.environment_variable.strip()
            if not normalized_environment_variable:
                raise SchemaDefinitionError(
                    f"Configuration field '{self.name}' has an empty environment variable name."
                )
            object.__setattr__(
                self,
                "environment_variable",
                normalized_environment_variable,
            )

        object.__setattr__(self, "name", normalized_name)
        object.__setattr__(self, "description", normalized_description)
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    @property
    def has_default(self) -> bool:
        """Return whether the field declares a default value."""
        return self.default is not UNSET

    @property
    def is_optional(self) -> bool:
        """Return whether the field may be omitted by configuration sources."""
        return not self.required


@dataclass(slots=True, frozen=True, kw_only=True)
class StringField(ConfigField):
    """Describe a field that resolves to a string value."""

    value_type: FieldRuntimeType = field(default=str, init=False)


@dataclass(slots=True, frozen=True, kw_only=True)
class IntegerField(ConfigField):
    """Describe a field that resolves to an integer value."""

    value_type: FieldRuntimeType = field(default=int, init=False)


@dataclass(slots=True, frozen=True, kw_only=True)
class FloatField(ConfigField):
    """Describe a field that resolves to a floating-point value."""

    value_type: FieldRuntimeType = field(default=float, init=False)


@dataclass(slots=True, frozen=True, kw_only=True)
class BooleanField(ConfigField):
    """Describe a field that resolves to a boolean value."""

    value_type: FieldRuntimeType = field(default=bool, init=False)


@dataclass(slots=True, frozen=True, kw_only=True)
class ListField(ConfigField):
    """Describe a field that resolves to a list value."""

    value_type: FieldRuntimeType = field(default=list, init=False)


@dataclass(slots=True, frozen=True, kw_only=True)
class MappingField(ConfigField):
    """Describe a field that resolves to a dictionary-like value."""

    value_type: FieldRuntimeType = field(default=dict, init=False)


@dataclass(slots=True, frozen=True, kw_only=True)
class SecretField(StringField):
    """Describe a string field containing sensitive data.

    Usage Notes:
        Secret redaction policy will be enforced in later milestones.
    """

    secret: bool = field(default=True, init=False)


@dataclass(slots=True, frozen=True, kw_only=True)
class PathField(ConfigField):
    """Describe a field representing a filesystem path.

    Attributes:
        path_rules: Declarative path-handling options for future normalization.
    """

    value_type: FieldRuntimeType = field(default=Path, init=False)
    path_rules: PathRules = field(default_factory=PathRules)
