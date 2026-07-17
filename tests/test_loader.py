"""Tests for high-level configuration loading orchestration."""

from __future__ import annotations

from dataclasses import dataclass, field

import pytest

import python_configuration_system.loader as loader_module
from python_configuration_system import (
    ConfigLoader,
    ConfigProfile,
    ConfigSchema,
    IntegerField,
    ProfileResolutionError,
    ResolvedConfig,
    SourceLoadError,
    StringField,
    ValidationError,
)
from python_configuration_system.errors import MergeConflictError
from python_configuration_system.sources.base import (
    ConfigSource,
    SourceDiscovery,
    SourceMetadata,
    SourcePayload,
)
from python_configuration_system.types import ConfigMapping, ProfileName, SourceName


@dataclass(slots=True)
class RecordingSource(ConfigSource):
    """Test source that records profile-aware load calls."""

    name: SourceName
    data: ConfigMapping
    loaded_profiles: list[ProfileName | None] = field(default_factory=list)

    @property
    def source_name(self) -> SourceName:
        """Return the source name used by diagnostics."""
        return self.name

    @property
    def metadata(self) -> SourceMetadata:
        """Return stable test metadata."""
        return SourceMetadata(
            source_name=self.source_name,
            kind="test",
            description="Test configuration source",
            supports_profiles=True,
        )

    def discover(
        self,
        *,
        profile_name: ProfileName | None = None,
    ) -> SourceDiscovery:
        """Return an empty discovery result for tests."""
        del profile_name
        return SourceDiscovery(metadata=self.metadata)

    def load(self, *, profile_name: ProfileName | None = None) -> SourcePayload:
        """Return configured test data and record the active profile."""
        self.loaded_profiles.append(profile_name)
        return SourcePayload(
            source_name=self.source_name,
            data=self.data,
            metadata=self.metadata,
        )


@dataclass(slots=True)
class FailingSource(ConfigSource):
    """Test source that raises the package source-load error."""

    name: SourceName = "failing"

    @property
    def source_name(self) -> SourceName:
        """Return the source name used by diagnostics."""
        return self.name

    @property
    def metadata(self) -> SourceMetadata:
        """Return stable test metadata."""
        return SourceMetadata(
            source_name=self.source_name,
            kind="test",
            description="Failing test source",
        )

    def discover(
        self,
        *,
        profile_name: ProfileName | None = None,
    ) -> SourceDiscovery:
        """Return an empty discovery result for tests."""
        del profile_name
        return SourceDiscovery(metadata=self.metadata)

    def load(self, *, profile_name: ProfileName | None = None) -> SourcePayload:
        """Raise a source-load error for propagation tests."""
        del profile_name
        raise SourceLoadError("Source failed during loading.")


def build_schema() -> ConfigSchema:
    """Create a schema shared by loader tests."""
    return ConfigSchema(
        name="service",
        fields=[
            StringField(name="service_name", description="Service name."),
            IntegerField(
                name="timeout_seconds",
                description="Timeout in seconds.",
                required=False,
                default=30,
            ),
        ],
    )


def test_loader_resolves_from_one_source() -> None:
    """Verify loader returns runtime config from a registered source."""
    loader = ConfigLoader(
        schema=build_schema(),
        sources=[RecordingSource(name="file", data={"service_name": "demo"})],
    )

    config = loader.resolve()

    assert isinstance(config, ResolvedConfig)
    assert config["service_name"] == "demo"
    assert config["timeout_seconds"] == 30
    assert config.source_names == ("file",)
    assert config.applied_defaults == ("timeout_seconds",)


def test_loader_uses_last_source_wins_precedence() -> None:
    """Verify later sources override earlier sources through merge behavior."""
    loader = ConfigLoader(
        schema=build_schema(),
        sources=[
            RecordingSource(name="file", data={"service_name": "demo"}),
            RecordingSource(name="env", data={"service_name": "prod"}),
        ],
    )

    config = loader.resolve()

    assert config["service_name"] == "prod"
    assert config.source_names == ("file", "env")


def test_loader_applies_overrides_with_highest_precedence() -> None:
    """Verify explicit overrides are merged after configured sources."""
    loader = ConfigLoader(
        schema=build_schema(),
        sources=[RecordingSource(name="file", data={"service_name": "demo"})],
    )

    config = loader.resolve(overrides={"service_name": "override"})

    assert config["service_name"] == "override"
    assert config.source_names == ("file", "overrides")


def test_loader_passes_profile_name_to_source_loading() -> None:
    """Verify active profile names flow through the source registry contract."""
    source = RecordingSource(name="file", data={"service_name": "demo"})
    loader = ConfigLoader(
        schema=build_schema(),
        sources=[source],
        profiles={"dev": ConfigProfile(name="dev")},
    )

    config = loader.resolve(profile_name="dev")

    assert source.loaded_profiles == ["dev"]
    assert config.profile_name == "dev"


def test_loader_rejects_unknown_profile() -> None:
    """Verify unknown profiles fail before source loading."""
    loader = ConfigLoader(
        schema=build_schema(),
        sources=[RecordingSource(name="file", data={"service_name": "demo"})],
    )

    with pytest.raises(ProfileResolutionError):
        loader.resolve(profile_name="missing")


def test_loader_rejects_unsupported_profile_inheritance() -> None:
    """Verify profile inheritance remains explicitly unsupported."""
    loader = ConfigLoader(
        schema=build_schema(),
        sources=[RecordingSource(name="file", data={"service_name": "demo"})],
        profiles={"prod": ConfigProfile(name="prod", extends="base")},
    )

    with pytest.raises(ProfileResolutionError):
        loader.resolve(profile_name="prod")


def test_loader_raises_validation_error_for_invalid_configuration() -> None:
    """Verify validation error reports block runtime creation."""
    loader = ConfigLoader(
        schema=build_schema(),
        sources=[RecordingSource(name="file", data={})],
    )

    with pytest.raises(ValidationError):
        loader.resolve()


def test_loader_preserves_source_load_errors() -> None:
    """Verify source loading failures keep their repository error type."""
    loader = ConfigLoader(schema=build_schema(), sources=[FailingSource()])

    with pytest.raises(SourceLoadError):
        loader.resolve()


def test_loader_preserves_merge_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify merge failures keep their repository error type."""

    class FailingMerger:
        """Test merger that raises the package merge error."""

        def merge(self, merge_input: object) -> object:
            """Raise a deterministic merge failure."""
            del merge_input
            raise MergeConflictError("Merge failed.")

    monkeypatch.setattr(loader_module, "ConfigMerger", FailingMerger)
    loader = ConfigLoader(
        schema=build_schema(),
        sources=[RecordingSource(name="file", data={"service_name": "demo"})],
    )

    with pytest.raises(MergeConflictError):
        loader.resolve()
