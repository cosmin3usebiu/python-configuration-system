"""Tests for deterministic merge behavior and structural merge metadata."""

from __future__ import annotations

from types import MappingProxyType

import pytest

from python_configuration_system.errors import MergeConflictError
from python_configuration_system.merge import ConfigMerger
from python_configuration_system.merge import LastSourceWinsMergeStrategy
from python_configuration_system.merge import MergeInput
from python_configuration_system.merge import MergeResult
from python_configuration_system.merge import StrictConflictMergeStrategy
from python_configuration_system.sources.base import SourcePayload


def test_merge_input_freezes_payload_order() -> None:
    """Verify merge inputs normalize payload collections into tuples."""
    merge_input = MergeInput(
        payloads=[
            SourcePayload(source_name="file", data={"service_name": "demo"}),
            SourcePayload(source_name="env", data={"service_name": "prod"}),
        ],
    )

    assert isinstance(merge_input.payloads, tuple)
    assert tuple(payload.source_name for payload in merge_input.payloads) == (
        "file",
        "env",
    )


def test_default_merge_strategy_uses_last_source_wins_precedence() -> None:
    """Verify later payloads override earlier payloads deterministically."""
    merge_result = ConfigMerger().merge(
        MergeInput(
            payloads=[
                SourcePayload(source_name="file", data={"service_name": "demo"}),
                SourcePayload(source_name="env", data={"service_name": "prod"}),
            ],
        )
    )

    assert merge_result.values["service_name"] == "prod"
    assert merge_result.source_names == ("file", "env")
    assert merge_result.diagnostics.field_origins["service_name"] == "env"
    assert merge_result.diagnostics.overridden_fields == ("service_name",)
    assert len(merge_result.diagnostics.conflicts) == 1


def test_merge_result_and_diagnostics_are_immutable() -> None:
    """Verify merged output is immutable for downstream consumers."""
    merge_result = ConfigMerger().merge(
        MergeInput(
            payloads=[SourcePayload(source_name="file", data={"service_name": "demo"})],
        )
    )

    assert isinstance(merge_result, MergeResult)
    assert isinstance(merge_result.values, MappingProxyType)
    assert isinstance(merge_result.diagnostics.field_origins, MappingProxyType)

    with pytest.raises(TypeError):
        merge_result.values["service_name"] = "prod"  # type: ignore[index]

    with pytest.raises(TypeError):
        merge_result.diagnostics.field_origins["service_name"] = "env"  # type: ignore[index]


def test_equal_repeated_values_do_not_create_conflicts() -> None:
    """Verify equal repeated values are treated as non-conflicting repeats."""
    merge_result = ConfigMerger(
        strategy=LastSourceWinsMergeStrategy(),
    ).merge(
        MergeInput(
            payloads=[
                SourcePayload(source_name="file", data={"service_name": "demo"}),
                SourcePayload(source_name="env", data={"service_name": "demo"}),
            ],
        )
    )

    assert merge_result.values["service_name"] == "demo"
    assert merge_result.diagnostics.overridden_fields == ()
    assert merge_result.diagnostics.conflicts == ()
    assert merge_result.diagnostics.field_origins["service_name"] == "file"


def test_strict_merge_strategy_raises_on_conflicting_values() -> None:
    """Verify strict conflict strategy rejects competing repeated values."""
    merger = ConfigMerger(strategy=StrictConflictMergeStrategy())

    with pytest.raises(MergeConflictError):
        merger.merge(
            MergeInput(
                payloads=[
                    SourcePayload(source_name="file", data={"service_name": "demo"}),
                    SourcePayload(source_name="env", data={"service_name": "prod"}),
                ],
            )
        )


def test_merge_engine_preserves_unknown_fields_without_validation() -> None:
    """Verify merge behavior remains payload-driven and schema-agnostic."""
    merge_result = ConfigMerger().merge(
        MergeInput(
            payloads=[
                SourcePayload(source_name="file", data={"service_name": "demo"}),
                SourcePayload(source_name="env", data={"extra_flag": "enabled"}),
            ],
        )
    )

    assert merge_result.values["service_name"] == "demo"
    assert merge_result.values["extra_flag"] == "enabled"
