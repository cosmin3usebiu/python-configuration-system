"""Environment-variable configuration source definitions."""

from __future__ import annotations

import os
from dataclasses import dataclass

from python_configuration_system.sources.base import (
    ConfigSource,
    SourceDiscovery,
    SourceMetadata,
    SourcePayload,
)
from python_configuration_system.types import ProfileName, SourceName


@dataclass(slots=True, frozen=True)
class EnvConfigSource(ConfigSource):
    """Load raw configuration values from environment variables.

    Purpose:
        Retrieve raw configuration data from the process environment using an
        optional variable prefix and a stable source identity.

    Parameters:
        name: Stable source name used for registration and diagnostics.
        prefix: Optional environment variable prefix used for filtering.
        description: Human-readable source description.

    Attributes:
        name: Stable source name.
        prefix: Optional environment variable prefix.
        description: Human-readable source description.

    Raises:
        SourceLoadError: If source metadata or loading state is invalid.

    Usage Notes:
        Loaded values remain raw strings. No type coercion or precedence logic
        is applied by this source.
    """

    name: SourceName = "env"
    prefix: str | None = None
    description: str = "Environment variable configuration source"

    @property
    def source_name(self) -> SourceName:
        """Return the stable source name for environment values."""
        return self.name

    @property
    def metadata(self) -> SourceMetadata:
        """Return descriptive metadata for the environment source."""
        return SourceMetadata(
            source_name=self.source_name,
            kind="environment",
            description=self.description,
            supports_profiles=False,
        )

    def discover(
        self,
        *,
        profile_name: ProfileName | None = None,
    ) -> SourceDiscovery:
        """Return matching environment variable names for the source.

        Args:
            profile_name: Optional profile name reserved for future use.

        Returns:
            Discovery information describing matched environment variables.
        """
        del profile_name
        return SourceDiscovery(
            metadata=self.metadata,
            locations=tuple(self._iter_matching_keys()),
        )

    def load(self, *, profile_name: ProfileName | None = None) -> SourcePayload:
        """Load values from environment variables.

        Args:
            profile_name: Optional active profile name.

        Returns:
            A raw source payload containing matched environment values.

        Raises:
            No additional exceptions are raised during normal loading.
        """
        del profile_name
        payload = {
            self._normalize_key(environment_key): os.environ[environment_key]
            for environment_key in self._iter_matching_keys()
        }
        return SourcePayload(
            source_name=self.source_name,
            data=payload,
            description=self.description,
            metadata=self.metadata,
        )

    def _iter_matching_keys(self) -> tuple[str, ...]:
        """Return environment variable names matching the configured prefix."""
        normalized_prefix = self.prefix.strip() if self.prefix is not None else None
        if normalized_prefix is None:
            matching_keys = tuple(sorted(os.environ))
        else:
            matching_keys = tuple(
                sorted(
                    environment_key
                    for environment_key in os.environ
                    if environment_key.startswith(normalized_prefix)
                )
            )
        return matching_keys

    def _normalize_key(self, environment_key: str) -> str:
        """Convert an environment variable name into a raw configuration key."""
        if self.prefix is None:
            normalized_key = environment_key
        else:
            normalized_key = environment_key.removeprefix(self.prefix)

        normalized_key = normalized_key.lstrip("_")
        return normalized_key.lower()
