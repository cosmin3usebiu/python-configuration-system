"""Tests for declarative schema and field definitions."""

from pathlib import Path

import pytest

from python_configuration_system import BooleanField
from python_configuration_system import ConfigSchema
from python_configuration_system import IntegerField
from python_configuration_system import PathField
from python_configuration_system import SchemaDefinitionError
from python_configuration_system import SecretField
from python_configuration_system import StringField
from python_configuration_system import UNSET
from python_configuration_system.paths import PathKind
from python_configuration_system.paths import PathRules


def test_string_field_defaults_to_required_without_default() -> None:
    """Verify the base string field declaration metadata."""
    field = StringField(
        name="api_base_url",
        description="Base URL for the remote service.",
    )

    assert field.name == "api_base_url"
    assert field.value_type is str
    assert field.required is True
    assert field.default is UNSET
    assert field.has_default is False
    assert field.is_optional is False


def test_optional_field_can_declare_default_none() -> None:
    """Verify an optional field can explicitly default to None."""
    field = StringField(
        name="profile_name",
        description="Optional profile selection.",
        required=False,
        default=None,
        allow_none=True,
    )

    assert field.required is False
    assert field.has_default is True
    assert field.default is None
    assert field.allow_none is True
    assert field.is_optional is True


def test_required_field_cannot_define_default() -> None:
    """Verify contradictory field definitions are rejected."""
    with pytest.raises(SchemaDefinitionError):
        IntegerField(
            name="request_timeout_seconds",
            description="Maximum request timeout.",
            default=30,
        )


def test_secret_field_marks_sensitive_metadata() -> None:
    """Verify the secret field specialization exposes secret metadata."""
    field = SecretField(
        name="api_token",
        description="Authentication token used by the application.",
    )

    assert field.secret is True
    assert field.value_type is str


def test_path_field_preserves_path_metadata() -> None:
    """Verify path field declarations retain path-specific rules."""
    rules = PathRules(kind=PathKind.DIRECTORY, must_exist=True)
    field = PathField(
        name="workspace_root",
        description="Workspace directory for generated artifacts.",
        required=False,
        path_rules=rules,
    )

    assert field.value_type is Path
    assert field.path_rules == rules


def test_schema_registers_fields_from_iterable() -> None:
    """Verify schemas can register fields from declaration order."""
    schema = ConfigSchema(
        name="service-config",
        description="Configuration for a simple service.",
        fields=[
            StringField(
                name="service_name",
                description="Public service identifier.",
            ),
            BooleanField(
                name="debug",
                description="Enable verbose debug mode.",
                required=False,
                default=False,
            ),
        ],
    )

    assert schema.field_names == ("service_name", "debug")
    assert schema.get_field("service_name") is not None
    assert schema.get_field("missing_field") is None


def test_schema_rejects_duplicate_field_names() -> None:
    """Verify iterable registration rejects duplicate field names."""
    with pytest.raises(SchemaDefinitionError):
        ConfigSchema(
            name="duplicate-fields",
            fields=[
                StringField(
                    name="service_name",
                    description="Primary service name.",
                ),
                StringField(
                    name="service_name",
                    description="Duplicate service name.",
                    required=False,
                ),
            ],
        )


def test_schema_rejects_mismatched_mapping_keys() -> None:
    """Verify mapping registration requires matching field names."""
    with pytest.raises(SchemaDefinitionError):
        ConfigSchema(
            name="invalid-mapping",
            fields={
                "service_label": StringField(
                    name="service_name",
                    description="Primary service name.",
                )
            },
        )
