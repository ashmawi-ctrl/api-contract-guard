from contract_guard.compare import compare_payloads
from contract_guard.models import Severity


def changes_by_kind(result, kind: str):
    return [change for change in result.changes if change.kind == kind]


def test_nested_object_to_string_is_breaking() -> None:
    baseline = {
        "history": [
            {
                "transactionResponseMessage": {
                    "en": "Settled",
                    "ar": "تم التسوية",
                }
            }
        ]
    }
    candidate = {
        "history": [
            {
                "transactionResponseMessage": "Settled",
            }
        ]
    }

    result = compare_payloads(baseline, candidate)

    assert result.has_breaking_changes is True
    change = changes_by_kind(result, "type_changed")[0]
    assert change.path == "$.history[0].transactionResponseMessage"
    assert change.severity is Severity.BREAKING


def test_removed_field_is_breaking() -> None:
    result = compare_payloads(
        {"id": "txn_1", "status": "success"},
        {"id": "txn_1"},
    )

    change = changes_by_kind(result, "field_removed")[0]
    assert change.path == "$.status"
    assert change.severity is Severity.BREAKING


def test_added_field_is_informational() -> None:
    result = compare_payloads(
        {"id": "txn_1"},
        {"id": "txn_1", "trace_id": "req_22"},
    )

    assert result.has_breaking_changes is False
    change = changes_by_kind(result, "field_added")[0]
    assert change.path == "$.trace_id"
    assert change.severity is Severity.INFO


def test_non_null_value_becoming_null_is_breaking_type_change() -> None:
    result = compare_payloads(
        {"merchant": {"name": "Example"}},
        {"merchant": {"name": None}},
    )

    change = changes_by_kind(result, "type_changed")[0]
    assert change.path == "$.merchant.name"
    assert "string to null" in change.message


def test_array_item_shape_is_compared() -> None:
    result = compare_payloads(
        {"items": [{"quantity": 1}]},
        {"items": [{"quantity": "1"}]},
    )

    change = changes_by_kind(result, "type_changed")[0]
    assert change.path == "$.items[0].quantity"


def test_candidate_empty_array_reports_warning_not_breaking() -> None:
    result = compare_payloads(
        {"items": [{"quantity": 1}]},
        {"items": []},
    )

    assert result.has_breaking_changes is False
    warning = changes_by_kind(result, "array_became_empty")[0]
    assert warning.severity is Severity.WARNING
