import json
from pathlib import Path

from contract_guard.cli import main


def write_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_cli_returns_two_for_breaking_change(
    tmp_path: Path,
    capsys,
) -> None:
    baseline = tmp_path / "baseline.json"
    candidate = tmp_path / "candidate.json"
    write_json(baseline, {"message": {"en": "Settled"}})
    write_json(candidate, {"message": "Settled"})

    exit_code = main([str(baseline), str(candidate)])

    assert exit_code == 2
    assert "[BREAKING]" in capsys.readouterr().out


def test_cli_json_mode_can_be_used_without_failing(
    tmp_path: Path,
    capsys,
) -> None:
    baseline = tmp_path / "baseline.json"
    candidate = tmp_path / "candidate.json"
    write_json(baseline, {"id": "txn_1"})
    write_json(candidate, {"id": "txn_1", "trace_id": "req_1"})

    exit_code = main(
        [
            str(baseline),
            str(candidate),
            "--format",
            "json",
        ]
    )

    assert exit_code == 0
    output = json.loads(capsys.readouterr().out)
    assert output["breaking"] is False
    assert output["changes"][0]["kind"] == "field_added"
