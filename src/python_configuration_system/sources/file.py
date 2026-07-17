"""File-based configuration source definitions."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from python_configuration_system.errors import SourceLoadError
from python_configuration_system.sources.base import ConfigSource
from python_configuration_system.sources.base import SourceDiscovery
from python_configuration_system.sources.base import SourceMetadata
from python_configuration_system.sources.base import SourcePayload
from python_configuration_system.types import ProfileName
from python_configuration_system.types import SourceName


@dataclass(slots=True, frozen=True)
class FileConfigSource(ConfigSource):
    """Load raw configuration values from a JSON configuration file.

    Purpose:
        Retrieve a raw top-level configuration mapping from a single JSON file
        while preserving source identity and metadata for later stages.

    Parameters:
        base_path: Path to the JSON configuration file.
        name: Stable source name used for registration and diagnostics.
        description: Human-readable source description.
        encoding: Text encoding used when reading the file.

    Attributes:
        base_path: Path to the JSON configuration file.
        name: Stable source name.
        description: Human-readable source description.
        encoding: Text encoding used for file reads.

    Raises:
        SourceLoadError: If the file is missing, unreadable, unsupported, or
            does not contain a top-level mapping.

    Usage Notes:
        This source only reads raw JSON object data. It does not validate
        field names or coerce value types.
    """

    base_path: Path
    name: SourceName = "file"
    description: str = "File configuration source"
    encoding: str = "utf-8"

    @property
    def source_name(self) -> SourceName:
        """Return the stable source name for file-based values."""
        return self.name

    @property
    def metadata(self) -> SourceMetadata:
        """Return descriptive metadata for the file source."""
        return SourceMetadata(
            source_name=self.source_name,
            kind="file",
            description=self.description,
            supports_profiles=False,
        )

    def discover(
        self,
        *,
        profile_name: ProfileName | None = None,
    ) -> SourceDiscovery:
        """Return the configured file path for discovery purposes.

        Args:
            profile_name: Optional profile name reserved for future use.

        Returns:
            Discovery information describing the configured file path.
        """
        del profile_name
        return SourceDiscovery(
            metadata=self.metadata,
            locations=(str(self.base_path),),
        )

    def load(self, *, profile_name: ProfileName | None = None) -> SourcePayload:
        """Load values from a configuration file.

        Args:
            profile_name: Optional active profile name.

        Returns:
            A raw source payload containing file-backed configuration values.

        Raises:
            SourceLoadError: If the file cannot be loaded safely.
        """
        del profile_name

        file_path = self.base_path

        if file_path.suffix.lower() != ".json":
            raise SourceLoadError(
                f"Configuration file source '{self.source_name}' only supports JSON files."
            )

        if not file_path.exists():
            raise SourceLoadError(
                f"Configuration file '{file_path}' does not exist for source "
                f"'{self.source_name}'."
            )

        try:
            with file_path.open("r", encoding=self.encoding) as file_handle:
                raw_data = json.load(file_handle)
        except OSError as exc:
            raise SourceLoadError(
                f"Configuration file '{file_path}' could not be read."
            ) from exc
        except json.JSONDecodeError as exc:
            raise SourceLoadError(
                f"Configuration file '{file_path}' does not contain valid JSON."
            ) from exc

        payload_data = self._validate_payload(raw_data)
        return SourcePayload(
            source_name=self.source_name,
            data=payload_data,
            description=self.description,
            metadata=self.metadata,
        )

    def _validate_payload(self, raw_data: Any) -> dict[str, Any]:
        """Ensure the parsed JSON payload is a top-level mapping."""
        if not isinstance(raw_data, dict):
            raise SourceLoadError(
                f"Configuration file source '{self.source_name}' requires a top-level "
                "JSON object."
            )
        return dict(raw_data)
