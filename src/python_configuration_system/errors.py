"""Custom exceptions for the configuration system package.

This module defines the public exception hierarchy for the package.
"""

from __future__ import annotations


class ConfigurationError(Exception):
    """Base exception for package-level configuration failures."""


class SchemaDefinitionError(ConfigurationError):
    """Raised when a schema definition is invalid."""


class SourceRegistrationError(ConfigurationError):
    """Represent source registry registration failures.

    Purpose:
        Signal that a configuration source cannot be registered into a source
        registry because its declaration conflicts with an existing source.

    Parameters:
        This exception accepts the standard ``Exception`` initialization
        arguments only.

    Attributes:
        No additional public attributes are defined.

    Raises:
        This class is raised by source registry operations and is not expected
        to raise additional exceptions itself.

    Usage Notes:
        Registration errors are structural problems in source composition, not
        source loading failures.
    """


class SourceLoadError(ConfigurationError):
    """Raised when a configuration source cannot be loaded."""


class ProfileResolutionError(ConfigurationError):
    """Raised when profile selection or profile inheritance fails."""


class MergeConflictError(ConfigurationError):
    """Raised when configuration values cannot be merged safely."""


class ValidationError(ConfigurationError):
    """Raised when resolved configuration data fails validation."""
