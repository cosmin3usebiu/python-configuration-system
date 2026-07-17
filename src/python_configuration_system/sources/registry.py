"""Source registration and discovery helpers.

This module defines the registry object responsible for keeping an ordered
collection of configuration sources discoverable and independently testable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

from python_configuration_system.errors import SourceRegistrationError
from python_configuration_system.sources.base import (
    ConfigSource,
    SourceDiscovery,
    SourcePayload,
)
from python_configuration_system.types import ProfileName, SourceName


@dataclass(slots=True, frozen=True)
class SourceRegistry:
    """Store and expose an ordered collection of configuration sources.

    Purpose:
        Provide a dedicated registration and discovery surface for
        configuration sources without coupling source composition to the future
        configuration loader.

    Parameters:
        sources: Ordered sequence of configuration source instances.

    Attributes:
        sources: Immutable ordered tuple of registered source instances.

    Raises:
        SourceRegistrationError: If duplicate source names are registered.

    Usage Notes:
        The registry preserves registration order but does not apply
        precedence, validation, or merge behavior.
    """

    sources: Sequence[ConfigSource] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        """Normalize registered sources and reject duplicate names."""
        normalized_sources = tuple(self.sources)
        source_names: set[SourceName] = set()

        for source in normalized_sources:
            if source.source_name in source_names:
                raise SourceRegistrationError(
                    f"Configuration source '{source.source_name}' is already "
                    "registered."
                )
            source_names.add(source.source_name)

        object.__setattr__(self, "sources", normalized_sources)

    @property
    def source_names(self) -> tuple[SourceName, ...]:
        """Return registered source names in registration order."""
        return tuple(source.source_name for source in self.sources)

    def register(self, source: ConfigSource) -> "SourceRegistry":
        """Return a new registry including an additional source.

        Args:
            source: Source instance to register.

        Returns:
            A new registry containing the existing sources and the new source.

        Raises:
            SourceRegistrationError: If the source name is already present.
        """
        return SourceRegistry((*self.sources, source))

    def get_source(self, source_name: SourceName) -> ConfigSource | None:
        """Return a registered source by name if it exists.

        Args:
            source_name: Stable source identifier.

        Returns:
            The matching source instance or ``None`` when absent.
        """
        for source in self.sources:
            if source.source_name == source_name:
                return source
        return None

    def discover(
        self,
        *,
        profile_name: ProfileName | None = None,
    ) -> tuple[SourceDiscovery, ...]:
        """Return discovery information for every registered source.

        Args:
            profile_name: Optional profile name reserved for future use.

        Returns:
            Ordered source discovery results.
        """
        return tuple(
            source.discover(profile_name=profile_name) for source in self.sources
        )

    def load(
        self,
        *,
        profile_name: ProfileName | None = None,
    ) -> tuple[SourcePayload, ...]:
        """Load raw configuration payloads from every registered source.

        Args:
            profile_name: Optional profile name reserved for future use.

        Returns:
            Ordered raw payloads from each registered source.
        """
        return tuple(source.load(profile_name=profile_name) for source in self.sources)
