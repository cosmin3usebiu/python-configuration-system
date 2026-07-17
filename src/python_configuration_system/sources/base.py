"""Base contracts for configuration sources.

This module defines the abstract source interface used by configuration source
implementations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from types import MappingProxyType

from python_configuration_system.types import ConfigMapping
from python_configuration_system.types import ProfileName
from python_configuration_system.types import SourceName


@dataclass(slots=True, frozen=True)
class SourceMetadata:
    """Describe source identity and capabilities.

    Purpose:
        Provide stable metadata for a configuration source without exposing the
        source implementation itself.

    Parameters:
        source_name: Stable source identifier used across the package.
        kind: High-level source category such as ``environment`` or ``file``.
        description: Human-readable source description.
        supports_profiles: Whether the source has profile-aware behavior.

    Attributes:
        source_name: Stable source identifier.
        kind: High-level source category.
        description: Human-readable description.
        supports_profiles: Whether profile-specific loading is supported.

    Raises:
        ValueError: If required metadata values are empty.

    Usage Notes:
        Metadata is descriptive only. It does not imply precedence or
        validation behavior.
    """

    source_name: SourceName
    kind: str
    description: str
    supports_profiles: bool = False

    def __post_init__(self) -> None:
        """Normalize metadata values and reject empty declarations."""
        normalized_name = self.source_name.strip()
        normalized_kind = self.kind.strip()
        normalized_description = self.description.strip()

        if not normalized_name:
            raise ValueError("Source metadata requires a non-empty source name.")

        if not normalized_kind:
            raise ValueError("Source metadata requires a non-empty kind.")

        if not normalized_description:
            raise ValueError("Source metadata requires a non-empty description.")

        object.__setattr__(self, "source_name", normalized_name)
        object.__setattr__(self, "kind", normalized_kind)
        object.__setattr__(self, "description", normalized_description)


@dataclass(slots=True, frozen=True)
class SourceDiscovery:
    """Describe how a source can currently be discovered.

    Purpose:
        Expose the raw discovery surface of a source, such as matching
        environment variables or the target file path, without loading or
        merging configuration values.

    Parameters:
        metadata: Stable source metadata.
        locations: Raw locations or identifiers associated with the source.

    Attributes:
        metadata: Stable descriptive source metadata.
        locations: Immutable tuple of discovered raw source identifiers.

    Raises:
        No additional exceptions are raised after successful construction.

    Usage Notes:
        Discovery is informational only and may return empty locations when no
        matching source input currently exists.
    """

    metadata: SourceMetadata
    locations: tuple[str, ...] = ()


@dataclass(slots=True, frozen=True)
class SourcePayload:
    """Represent raw configuration values loaded from a single source.

    Purpose:
        Carry raw, source-scoped configuration data into later merge and
        validation stages without embedding source implementation details.

    Parameters:
        source_name: Stable source identifier used in diagnostics and ordering.
        data: Raw key-value configuration mapping loaded from the source.
        description: Human-readable source description.
        metadata: Optional stable source metadata.

    Attributes:
        source_name: Stable source identifier.
        data: Immutable top-level mapping of raw configuration values.
        description: Human-readable source description.
        metadata: Stable descriptive source metadata when available.

    Raises:
        ValueError: If the source name is empty.

    Usage Notes:
        Payloads preserve raw source values and do not perform validation,
        precedence, or business-specific transformation.
    """

    source_name: SourceName
    data: ConfigMapping
    description: str = ""
    metadata: SourceMetadata | None = None

    def __post_init__(self) -> None:
        """Normalize payload metadata and freeze the top-level mapping."""
        normalized_name = self.source_name.strip()
        normalized_description = self.description.strip()

        if not normalized_name:
            raise ValueError("Source payloads require a non-empty source name.")

        object.__setattr__(self, "source_name", normalized_name)
        object.__setattr__(self, "description", normalized_description)
        object.__setattr__(self, "data", MappingProxyType(dict(self.data)))


class ConfigSource(ABC):
    """Define the public contract for raw configuration sources.

    Purpose:
        Standardize how configuration data sources describe themselves, expose
        discovery information, and load raw configuration mappings.

    Parameters:
        This abstract interface does not define constructor parameters.

    Attributes:
        Implementations must expose stable source metadata and a stable source
        name.

    Raises:
        Implementations may raise ``SourceLoadError`` during source loading.

    Usage Notes:
        Source implementations must only retrieve raw configuration data. They
        must not apply precedence, validation, or business-specific mapping.
    """

    @property
    @abstractmethod
    def source_name(self) -> SourceName:
        """Return the stable source name used in diagnostics."""

    @property
    @abstractmethod
    def metadata(self) -> SourceMetadata:
        """Return stable descriptive metadata for the source."""

    @abstractmethod
    def discover(
        self,
        *,
        profile_name: ProfileName | None = None,
    ) -> SourceDiscovery:
        """Return discovery information for the source.

        Args:
            profile_name: Optional profile name reserved for future use.

        Returns:
            Raw discovery information for the source.
        """

    @abstractmethod
    def load(self, *, profile_name: ProfileName | None = None) -> SourcePayload:
        """Load configuration values from the source.

        Args:
            profile_name: Optional active profile name.

        Returns:
            A raw source payload.

        Raises:
            NotImplementedError: Always for abstract contracts.
        """
