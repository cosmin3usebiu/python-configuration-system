"""High-level configuration loading orchestration.

This module defines the public loader interface used to coordinate schema,
sources, profiles, validation, and runtime resolution.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Sequence

from python_configuration_system.profiles import ConfigProfile
from python_configuration_system.runtime import ResolvedConfig
from python_configuration_system.schema import ConfigSchema
from python_configuration_system.sources.base import ConfigSource
from python_configuration_system.types import ConfigMapping, ProfileName


@dataclass(slots=True)
class ConfigLoader:
    """Coordinate end-to-end configuration resolution.

    Attributes:
        schema: Schema describing the application's configuration contract.
        sources: Ordered collection of configuration sources.
        profiles: Optional profile registry keyed by profile name.

    Usage Notes:
        This loader is intentionally non-operational during Milestone 2. The
        interface is established now so later milestones can implement behavior
        without redesigning the public API.
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
            A future immutable runtime configuration object.

        Raises:
            NotImplementedError: Always raised during Milestone 2.
        """

        raise NotImplementedError("Configuration resolution is not implemented yet.")
