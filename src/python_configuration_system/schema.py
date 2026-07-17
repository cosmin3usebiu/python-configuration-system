"""Schema definitions for the configuration system.

This module defines the immutable top-level schema object used to describe the
shape of an application's configuration surface.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Iterable, Mapping

from python_configuration_system.errors import SchemaDefinitionError
from python_configuration_system.fields import ConfigField
from python_configuration_system.types import FieldName


@dataclass(slots=True, frozen=True, kw_only=True)
class ConfigSchema:
    """Describe an application's configuration schema.

    Attributes:
        name: Human-readable schema name used in diagnostics.
        fields: Mapping or iterable of field definitions registered by name.
        description: Optional schema description for documentation output.

    Raises:
        SchemaDefinitionError: If schema registration metadata is invalid.

    Usage Notes:
        This class is a declarative definition only during Milestone 3. It does
        not perform loading, merge, or validation behavior.
    """

    name: str
    fields: Mapping[FieldName, ConfigField] | Iterable[ConfigField]
    description: str = ""

    def __post_init__(self) -> None:
        """Normalize schema metadata and register the field collection."""
        normalized_name = self.name.strip()
        normalized_description = self.description.strip()

        if not normalized_name:
            raise SchemaDefinitionError("Configuration schema names must be non-empty.")

        object.__setattr__(self, "name", normalized_name)
        object.__setattr__(self, "description", normalized_description)
        object.__setattr__(self, "fields", self._register_fields(self.fields))

    @property
    def field_names(self) -> tuple[FieldName, ...]:
        """Return the registered field names in declaration order."""
        return tuple(self.fields.keys())

    def get_field(self, field_name: FieldName) -> ConfigField | None:
        """Return a registered field by name if it exists."""
        return self.fields.get(field_name)

    def _register_fields(
        self,
        fields: Mapping[FieldName, ConfigField] | Iterable[ConfigField],
    ) -> Mapping[FieldName, ConfigField]:
        """Normalize schema fields into an immutable registration mapping."""
        if isinstance(fields, Mapping):
            registered_fields: dict[FieldName, ConfigField] = {}
            for field_name, config_field in fields.items():
                if field_name != config_field.name:
                    raise SchemaDefinitionError(
                        "Schema field mapping keys must match field names. "
                        f"Received key '{field_name}' for field '{config_field.name}'."
                    )
                registered_fields[field_name] = config_field
            return MappingProxyType(registered_fields)

        registered_fields = {}
        for config_field in fields:
            if config_field.name in registered_fields:
                raise SchemaDefinitionError(
                    f"Configuration schema '{self.name}' contains duplicate field "
                    f"'{config_field.name}'."
                )
            registered_fields[config_field.name] = config_field

        return MappingProxyType(registered_fields)
