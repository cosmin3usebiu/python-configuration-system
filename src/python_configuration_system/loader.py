"""High-level configuration loading orchestration.

This module defines the public loader interface used to coordinate schema,
sources, profiles, validation, and runtime resolution.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Sequence

from python_configuration_system.errors import ProfileResolutionError, ValidationError
from python_configuration_system.merge import ConfigMerger, MergeInput
from python_configuration_system.profiles import ConfigProfile
from python_configuration_system.runtime import ResolvedConfig
from python_configuration_system.schema import ConfigSchema
from python_configuration_system.sources.base import ConfigSource, SourcePayload
from python_configuration_system.sources.registry import SourceRegistry
from python_configuration_system.types import ConfigMapping, ProfileName
from python_configuration_system.validate import ConfigValidator, ValidationSeverity


@dataclass(slots=True)
class ConfigLoader:
    """Coordinate end-to-end configuration resolution.

    Attributes:
        schema: Schema describing the application's configuration contract.
        sources: Ordered collection of configuration sources.
        profiles: Optional profile registry keyed by profile name.

    Usage Notes:
        This loader is intentionally limited to orchestration. Source loading,
        merge behavior, validation, and runtime projection remain owned by
        their dedicated modules.
    """

    schema: ConfigSchema
    sources: Sequence[ConfigSource]
    profiles: Mapping[ProfileName, ConfigProfile] = field(default_factory=dict)

    def resolve(
        self,
        *,
        profile_name: ProfileName | None = None,
        overrides: ConfigMapping | None = None,
    ) -> ResolvedConfig:
        """Resolve configuration for an application.

        Args:
            profile_name: Optional explicit profile name.
            overrides: Optional explicit runtime overrides.

        Returns:
            An immutable runtime configuration object.

        Raises:
            ProfileResolutionError: If a requested profile is unknown or uses
                unsupported inheritance.
            ValidationError: If schema validation reports error-severity issues.
        """

        resolved_profile_name = self._resolve_profile_name(profile_name)
        payloads = list(
            SourceRegistry(self.sources).load(profile_name=resolved_profile_name)
        )

        if overrides is not None:
            payloads.append(
                SourcePayload(
                    source_name="overrides",
                    data=dict(overrides),
                    description="Explicit runtime overrides",
                )
            )

        merge_result = ConfigMerger().merge(
            MergeInput(
                payloads=tuple(payloads),
                profile_name=resolved_profile_name,
            )
        )
        validation_report = ConfigValidator().validate(
            schema=self.schema,
            merge_result=merge_result,
        )

        error_issues = tuple(
            issue
            for issue in validation_report.issues
            if issue.severity == ValidationSeverity.ERROR
        )
        if error_issues:
            issue_summary = ", ".join(
                f"{issue.code}:{issue.field_name}" for issue in error_issues
            )
            raise ValidationError(
                "Configuration validation failed with "
                f"{len(error_issues)} error(s): {issue_summary}."
            )

        return ResolvedConfig.from_validation_report(
            validation_report=validation_report,
            profile_name=resolved_profile_name,
        )

    def _resolve_profile_name(
        self,
        profile_name: ProfileName | None,
    ) -> ProfileName | None:
        """Validate the requested profile and return the resolved profile name."""
        if profile_name is None:
            return None

        profile = self.profiles.get(profile_name)
        if profile is None:
            raise ProfileResolutionError(
                f"Configuration profile '{profile_name}' is not registered."
            )

        if profile.extends is not None:
            raise ProfileResolutionError(
                "Configuration profile inheritance is not implemented for "
                f"profile '{profile_name}'."
            )

        return profile.name
