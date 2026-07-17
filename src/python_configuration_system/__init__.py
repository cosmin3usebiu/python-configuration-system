"""Public package interface for python-configuration-system.

This module exposes the stable public object model for the repository.
Operational behavior is intentionally deferred to later milestones.
"""

from python_configuration_system import errors
from python_configuration_system import diagnostics
from python_configuration_system import fields
from python_configuration_system import loader
from python_configuration_system import profiles
from python_configuration_system import runtime
from python_configuration_system import schema
from python_configuration_system import sources
from python_configuration_system import validate

ConfigurationError = errors.ConfigurationError
MergeConflictError = errors.MergeConflictError
ProfileResolutionError = errors.ProfileResolutionError
SchemaDefinitionError = errors.SchemaDefinitionError
SourceLoadError = errors.SourceLoadError
SourceRegistrationError = errors.SourceRegistrationError
ValidationError = errors.ValidationError
BooleanField = fields.BooleanField
ConfigField = fields.ConfigField
FloatField = fields.FloatField
IntegerField = fields.IntegerField
ListField = fields.ListField
MappingField = fields.MappingField
PathField = fields.PathField
SecretField = fields.SecretField
StringField = fields.StringField
UNSET = fields.UNSET
ConfigLoader = loader.ConfigLoader
ConfigProfile = profiles.ConfigProfile
ResolvedConfig = runtime.ResolvedConfig
ConfigSchema = schema.ConfigSchema
ConfigSource = sources.ConfigSource
EnvConfigSource = sources.EnvConfigSource
FileConfigSource = sources.FileConfigSource
SourceDiscovery = sources.SourceDiscovery
SourceMetadata = sources.SourceMetadata
SourcePayload = sources.SourcePayload
SourceRegistry = sources.SourceRegistry
ConfigValidator = validate.ConfigValidator
ValidationIssue = validate.ValidationIssue
ValidationReport = validate.ValidationReport
ValidationSeverity = validate.ValidationSeverity
ConfigurationSummary = diagnostics.ConfigurationSummary
DiagnosticsFormatter = diagnostics.DiagnosticsFormatter
DiagnosticsMode = diagnostics.DiagnosticsMode
ValidationStatistics = diagnostics.ValidationStatistics

__all__ = [
    "BooleanField",
    "ConfigField",
    "ConfigLoader",
    "ConfigProfile",
    "ConfigSchema",
    "ConfigSource",
    "ConfigValidator",
    "ConfigurationSummary",
    "ConfigurationError",
    "DiagnosticsFormatter",
    "DiagnosticsMode",
    "EnvConfigSource",
    "FloatField",
    "FileConfigSource",
    "IntegerField",
    "ListField",
    "MappingField",
    "MergeConflictError",
    "PathField",
    "ProfileResolutionError",
    "ResolvedConfig",
    "SchemaDefinitionError",
    "SecretField",
    "SourceDiscovery",
    "SourceLoadError",
    "SourceMetadata",
    "SourcePayload",
    "SourceRegistrationError",
    "SourceRegistry",
    "StringField",
    "UNSET",
    "ValidationError",
    "ValidationIssue",
    "ValidationReport",
    "ValidationSeverity",
    "ValidationStatistics",
]
