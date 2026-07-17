"""Configuration merge operations and precedence handling.

This module defines the merge contract used to combine raw source payloads
into a single configuration mapping according to deterministic precedence
rules.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping, Sequence

from python_configuration_system.errors import MergeConflictError
from python_configuration_system.sources.base import SourcePayload
from python_configuration_system.types import ConfigMapping
from python_configuration_system.types import ConfigValue
from python_configuration_system.types import FieldName
from python_configuration_system.types import ProfileName
from python_configuration_system.types import SourceName


@dataclass(slots=True, frozen=True)
class MergeInput:
    """Describe the inputs required to perform a merge operation.

    Purpose:
        Carry the raw merge inputs passed into the merge engine while keeping
        the merge contract explicit and independently testable.

    Parameters:
        payloads: Ordered raw source payloads to merge.
        profile_name: Optional profile name reserved for future orchestration.

    Attributes:
        payloads: Immutable ordered source payloads.
        profile_name: Optional profile name reserved for future use.

    Raises:
        No additional exceptions are raised after successful construction.

    Usage Notes:
        Merge behavior is driven by payload order. This object does not perform
        validation or precedence resolution itself.

    Example:
        >>> from python_configuration_system.sources.base import SourcePayload
        >>> merge_input = MergeInput(
        ...     payloads=[SourcePayload(source_name="env", data={"service_name": "demo"})],
        ... )
        >>> len(merge_input.payloads)
        1
    """

    payloads: Sequence[SourcePayload]
    profile_name: ProfileName | None = None

    def __post_init__(self) -> None:
        """Freeze the payload sequence for deterministic merging."""
        object.__setattr__(self, "payloads", tuple(self.payloads))


@dataclass(slots=True, frozen=True)
class MergeConflict:
    """Describe a precedence conflict encountered during merge.

    Purpose:
        Record the structural details of a repeated field assignment without
        formatting diagnostics or making validation decisions.

    Parameters:
        field_name: Field affected by the conflict.
        existing_source_name: Source that previously supplied the field value.
        incoming_source_name: Source that supplied the competing field value.
        existing_value: Previously merged field value.
        incoming_value: Incoming competing field value.
        resolution: Human-readable summary of how the conflict was resolved.

    Attributes:
        field_name: Field affected by the conflict.
        existing_source_name: Source that previously supplied the field value.
        incoming_source_name: Source that supplied the competing field value.
        existing_value: Previously merged field value.
        incoming_value: Incoming competing field value.
        resolution: Human-readable conflict resolution summary.

    Raises:
        No additional exceptions are raised after successful construction.

    Usage Notes:
        Conflict records are structural metadata only. They do not imply that
        the merge operation failed.

    Example:
        >>> conflict = MergeConflict(
        ...     field_name="timeout_seconds",
        ...     existing_source_name="file",
        ...     incoming_source_name="env",
        ...     existing_value=30,
        ...     incoming_value=10,
        ...     resolution="incoming value replaced existing value",
        ... )
        >>> conflict.field_name
        'timeout_seconds'
    """

    field_name: FieldName
    existing_source_name: SourceName
    incoming_source_name: SourceName
    existing_value: ConfigValue
    incoming_value: ConfigValue
    resolution: str


@dataclass(slots=True, frozen=True)
class MergeOutcome:
    """Describe the strategy decision for a repeated field assignment.

    Purpose:
        Carry the result of a merge strategy decision back to the merge engine
        without exposing strategy internals.

    Parameters:
        value: Value selected by the merge strategy.
        source_name: Source associated with the selected value.
        overridden: Whether an existing merged value was replaced.
        conflict: Structural conflict information, when applicable.

    Attributes:
        value: Value selected by the merge strategy.
        source_name: Source associated with the selected value.
        overridden: Whether an existing merged value was replaced.
        conflict: Structural conflict information, when applicable.

    Raises:
        No additional exceptions are raised after successful construction.

    Usage Notes:
        Outcomes are strategy-local decisions. They do not format diagnostics
        or mutate merge state directly.

    Example:
        >>> outcome = MergeOutcome(value="env", source_name="env", overridden=True)
        >>> outcome.overridden
        True
    """

    value: ConfigValue
    source_name: SourceName
    overridden: bool = False
    conflict: MergeConflict | None = None


@dataclass(slots=True, frozen=True)
class MergeDiagnostics:
    """Describe structural metadata produced by a merge operation.

    Purpose:
        Preserve merge metadata for later stages without formatting diagnostics
        or binding the merge engine to runtime inspection concerns.

    Parameters:
        source_names: Ordered source names participating in the merge.
        field_origins: Final source associated with each merged field.
        overridden_fields: Ordered field names that were overridden.
        conflicts: Structural conflict records encountered during merge.

    Attributes:
        source_names: Ordered source names participating in the merge.
        field_origins: Immutable mapping of field names to final source names.
        overridden_fields: Ordered field names that were overridden.
        conflicts: Ordered structural conflict records.

    Raises:
        No additional exceptions are raised after successful construction.

    Usage Notes:
        This metadata is descriptive only. It does not format output or alter
        merge behavior.

    Example:
        >>> diagnostics = MergeDiagnostics(
        ...     source_names=("file", "env"),
        ...     field_origins={"timeout_seconds": "env"},
        ...     overridden_fields=("timeout_seconds",),
        ... )
        >>> diagnostics.field_origins["timeout_seconds"]
        'env'
    """

    source_names: tuple[SourceName, ...]
    field_origins: Mapping[FieldName, SourceName]
    overridden_fields: tuple[FieldName, ...] = ()
    conflicts: tuple[MergeConflict, ...] = ()

    def __post_init__(self) -> None:
        """Freeze merge metadata for downstream consumers."""
        object.__setattr__(self, "source_names", tuple(self.source_names))
        object.__setattr__(
            self,
            "field_origins",
            MappingProxyType(dict(self.field_origins)),
        )
        object.__setattr__(self, "overridden_fields", tuple(self.overridden_fields))
        object.__setattr__(self, "conflicts", tuple(self.conflicts))


@dataclass(slots=True, frozen=True)
class MergeResult:
    """Describe the result of a merge operation.

    Purpose:
        Expose the immutable merged configuration mapping and its structural
        merge metadata to later stages of the configuration pipeline.

    Parameters:
        values: Final merged configuration mapping.
        source_names: Ordered source names participating in the merge.
        diagnostics: Structural merge metadata.

    Attributes:
        values: Immutable merged configuration mapping.
        source_names: Ordered source names participating in the merge.
        diagnostics: Structural merge metadata.

    Raises:
        No additional exceptions are raised after successful construction.

    Usage Notes:
        Merge results are data objects only. They do not perform validation,
        runtime projection, or diagnostics formatting.

    Example:
        >>> result = MergeResult(
        ...     values={"service_name": "demo"},
        ...     source_names=("file",),
        ...     diagnostics=MergeDiagnostics(
        ...         source_names=("file",),
        ...         field_origins={"service_name": "file"},
        ...     ),
        ... )
        >>> result.values["service_name"]
        'demo'
    """

    values: ConfigMapping
    source_names: tuple[SourceName, ...]
    diagnostics: MergeDiagnostics

    def __post_init__(self) -> None:
        """Freeze merged data for downstream consumers."""
        object.__setattr__(self, "values", MappingProxyType(dict(self.values)))
        object.__setattr__(self, "source_names", tuple(self.source_names))


class MergeStrategy(ABC):
    """Define the contract for repeated-field merge strategies.

    Purpose:
        Separate precedence decisions from merge iteration so different merge
        policies can be applied without changing the merge engine itself.

    Parameters:
        This abstract strategy does not define constructor parameters.

    Attributes:
        Concrete implementations own the precedence behavior for repeated
        field assignments.

    Raises:
        Concrete implementations may raise ``MergeConflictError`` when they
        choose not to resolve a repeated assignment.

    Usage Notes:
        Strategies decide only how repeated keys are handled. They do not load
        sources, validate values, or mutate merge state directly.

    Example:
        >>> strategy = LastSourceWinsMergeStrategy()
        >>> isinstance(strategy, MergeStrategy)
        True
    """

    @abstractmethod
    def resolve(
        self,
        *,
        field_name: FieldName,
        existing_value: ConfigValue,
        existing_source_name: SourceName,
        incoming_value: ConfigValue,
        incoming_source_name: SourceName,
    ) -> MergeOutcome:
        """Resolve a repeated field assignment.

        Args:
            field_name: Repeated field name.
            existing_value: Value currently present in the merged mapping.
            existing_source_name: Source of the existing value.
            incoming_value: New incoming competing value.
            incoming_source_name: Source of the incoming value.

        Returns:
            Strategy decision for the repeated assignment.
        """


class LastSourceWinsMergeStrategy(MergeStrategy):
    """Resolve repeated fields by preferring the later payload.

    Purpose:
        Apply deterministic last-source-wins precedence while preserving
        structural conflict metadata for later inspection.

    Parameters:
        This strategy does not define constructor parameters.

    Attributes:
        No additional public attributes are defined.

    Raises:
        No additional exceptions are raised during normal operation.

    Usage Notes:
        The strategy only replaces the value when a later payload repeats an
        existing field. Equal values are treated as non-conflicting repeats.

    Example:
        >>> strategy = LastSourceWinsMergeStrategy()
        >>> outcome = strategy.resolve(
        ...     field_name="timeout_seconds",
        ...     existing_value=30,
        ...     existing_source_name="file",
        ...     incoming_value=10,
        ...     incoming_source_name="env",
        ... )
        >>> outcome.value
        10
    """

    def resolve(
        self,
        *,
        field_name: FieldName,
        existing_value: ConfigValue,
        existing_source_name: SourceName,
        incoming_value: ConfigValue,
        incoming_source_name: SourceName,
    ) -> MergeOutcome:
        """Resolve a repeated assignment using last-source-wins precedence."""
        if existing_value == incoming_value:
            return MergeOutcome(
                value=existing_value,
                source_name=existing_source_name,
            )

        conflict = MergeConflict(
            field_name=field_name,
            existing_source_name=existing_source_name,
            incoming_source_name=incoming_source_name,
            existing_value=existing_value,
            incoming_value=incoming_value,
            resolution="incoming value replaced existing value",
        )
        return MergeOutcome(
            value=incoming_value,
            source_name=incoming_source_name,
            overridden=True,
            conflict=conflict,
        )


class StrictConflictMergeStrategy(MergeStrategy):
    """Reject repeated fields when competing values differ.

    Purpose:
        Provide a strict merge policy for callers that want conflicting values
        to fail instead of resolving through precedence.

    Parameters:
        This strategy does not define constructor parameters.

    Attributes:
        No additional public attributes are defined.

    Raises:
        MergeConflictError: If competing repeated values differ.

    Usage Notes:
        Equal repeated values are accepted and treated as a no-op.

    Example:
        >>> strategy = StrictConflictMergeStrategy()
        >>> outcome = strategy.resolve(
        ...     field_name="timeout_seconds",
        ...     existing_value=30,
        ...     existing_source_name="file",
        ...     incoming_value=30,
        ...     incoming_source_name="env",
        ... )
        >>> outcome.value
        30
    """

    def resolve(
        self,
        *,
        field_name: FieldName,
        existing_value: ConfigValue,
        existing_source_name: SourceName,
        incoming_value: ConfigValue,
        incoming_source_name: SourceName,
    ) -> MergeOutcome:
        """Resolve a repeated assignment by rejecting conflicting values."""
        if existing_value == incoming_value:
            return MergeOutcome(
                value=existing_value,
                source_name=existing_source_name,
            )

        raise MergeConflictError(
            "Conflicting values encountered for field "
            f"'{field_name}' from sources '{existing_source_name}' "
            f"and '{incoming_source_name}'."
        )


@dataclass(slots=True)
class ConfigMerger:
    """Merge raw source payloads into a single configuration mapping.

    Purpose:
        Coordinate payload iteration, deterministic precedence application, and
        structural merge metadata collection without performing validation or
        runtime projection.

    Parameters:
        strategy: Strategy used when repeated fields are encountered.

    Attributes:
        strategy: Strategy used when repeated fields are encountered.

    Raises:
        MergeConflictError: If the configured strategy rejects a repeated
            field assignment.

    Usage Notes:
        The merge engine is intentionally top-level only in this milestone.
        Nested structures are treated as raw values and replaced as a whole.

    Example:
        >>> from python_configuration_system.sources.base import SourcePayload
        >>> merger = ConfigMerger()
        >>> merge_result = merger.merge(
        ...     MergeInput(
        ...         payloads=[
        ...             SourcePayload(source_name="file", data={"service_name": "demo"}),
        ...             SourcePayload(source_name="env", data={"service_name": "prod"}),
        ...         ],
        ...     )
        ... )
        >>> merge_result.values["service_name"]
        'prod'
    """

    strategy: MergeStrategy = field(default_factory=LastSourceWinsMergeStrategy)

    def merge(self, merge_input: MergeInput) -> MergeResult:
        """Combine source payloads into a merged configuration candidate.

        Args:
            merge_input: Structured merge inputs.

        Returns:
            Immutable merged mapping and structural merge metadata.

        Raises:
            MergeConflictError: If the configured strategy rejects a repeated
                field assignment.
        """
        merged_values: dict[FieldName, ConfigValue] = {}
        field_origins: dict[FieldName, SourceName] = {}
        source_names = tuple(payload.source_name for payload in merge_input.payloads)
        overridden_fields: list[FieldName] = []
        overridden_field_names: set[FieldName] = set()
        conflicts: list[MergeConflict] = []

        for payload in merge_input.payloads:
            for field_name, incoming_value in payload.data.items():
                if field_name not in merged_values:
                    merged_values[field_name] = incoming_value
                    field_origins[field_name] = payload.source_name
                    continue

                outcome = self.strategy.resolve(
                    field_name=field_name,
                    existing_value=merged_values[field_name],
                    existing_source_name=field_origins[field_name],
                    incoming_value=incoming_value,
                    incoming_source_name=payload.source_name,
                )
                merged_values[field_name] = outcome.value
                field_origins[field_name] = outcome.source_name

                if outcome.overridden and field_name not in overridden_field_names:
                    overridden_fields.append(field_name)
                    overridden_field_names.add(field_name)

                if outcome.conflict is not None:
                    conflicts.append(outcome.conflict)

        diagnostics = MergeDiagnostics(
            source_names=source_names,
            field_origins=field_origins,
            overridden_fields=tuple(overridden_fields),
            conflicts=tuple(conflicts),
        )
        return MergeResult(
            values=merged_values,
            source_names=source_names,
            diagnostics=diagnostics,
        )
