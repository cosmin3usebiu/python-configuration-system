"""Basic repository smoke tests for the package skeleton."""

from importlib import import_module


def test_package_can_be_imported() -> None:
    """Verify that the package namespace is available."""
    module = import_module("python_configuration_system")
    assert module is not None


def test_public_exports_are_available() -> None:
    """Verify that the documented public exports exist."""
    module = import_module("python_configuration_system")
    assert hasattr(module, "ConfigField")
    assert hasattr(module, "ConfigLoader")
    assert hasattr(module, "ConfigProfile")
    assert hasattr(module, "ConfigSchema")
    assert hasattr(module, "ConfigValidator")
    assert hasattr(module, "DiagnosticsFormatter")
    assert hasattr(module, "EnvConfigSource")
    assert hasattr(module, "FileConfigSource")
    assert hasattr(module, "ResolvedConfig")
    assert hasattr(module, "SourceRegistry")
    assert hasattr(module, "StringField")
    assert hasattr(module, "UNSET")
