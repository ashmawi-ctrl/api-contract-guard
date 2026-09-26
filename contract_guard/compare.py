from collections.abc import Mapping, Sequence
from typing import Any

from .models import ComparisonResult, ContractChange, Severity


def compare_payloads(baseline: Any, candidate: Any) -> ComparisonResult:
    changes: list[ContractChange] = []
    _compare_node(baseline, candidate, "$", changes)
    return ComparisonResult(tuple(changes))


def json_type(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, str):
        return "string"
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return "number"
    if isinstance(value, Mapping):
        return "object"
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return "array"
    return type(value).__name__


def _compare_node(
    baseline: Any,
    candidate: Any,
    path: str,
    changes: list[ContractChange],
) -> None:
    baseline_type = json_type(baseline)
    candidate_type = json_type(candidate)

    if baseline_type != candidate_type:
        changes.append(
            ContractChange(
                path=path,
                severity=Severity.BREAKING,
                kind="type_changed",
                message=(
                    f"type changed from {baseline_type} to {candidate_type}"
                ),
            )
        )
        return

    if baseline_type == "object":
        _compare_objects(baseline, candidate, path, changes)
        return

    if baseline_type == "array":
        _compare_arrays(baseline, candidate, path, changes)


def _compare_objects(
    baseline: Mapping[str, Any],
    candidate: Mapping[str, Any],
    path: str,
    changes: list[ContractChange],
) -> None:
    baseline_keys = set(baseline)
    candidate_keys = set(candidate)

    for key in sorted(baseline_keys - candidate_keys):
        changes.append(
            ContractChange(
                path=_child_path(path, key),
                severity=Severity.BREAKING,
                kind="field_removed",
                message="field is missing from candidate payload",
            )
        )

    for key in sorted(candidate_keys - baseline_keys):
        changes.append(
            ContractChange(
                path=_child_path(path, key),
                severity=Severity.INFO,
                kind="field_added",
                message="new field added to candidate payload",
            )
        )

    for key in sorted(baseline_keys & candidate_keys):
        _compare_node(
            baseline[key],
            candidate[key],
            _child_path(path, key),
            changes,
        )


def _compare_arrays(
    baseline: Sequence[Any],
    candidate: Sequence[Any],
    path: str,
    changes: list[ContractChange],
) -> None:
    if baseline and not candidate:
        changes.append(
            ContractChange(
                path=path,
                severity=Severity.WARNING,
                kind="array_became_empty",
                message=(
                    "candidate array is empty, so item compatibility "
                    "cannot be verified"
                ),
            )
        )
        return

    if not baseline or not candidate:
        return

    _compare_node(
        baseline[0],
        candidate[0],
        f"{path}[0]",
        changes,
    )


def _child_path(parent: str, key: str) -> str:
    if key.isidentifier():
        return f"{parent}.{key}"
    return f"{parent}[{key!r}]"
