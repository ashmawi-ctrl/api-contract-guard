import argparse
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .compare import compare_payloads


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="api-contract-guard",
        description=(
            "Compare two JSON payloads and report structural API contract drift."
        ),
    )
    parser.add_argument("baseline", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        dest="output_format",
    )
    parser.add_argument(
        "--fail-on-breaking",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Exit with status 2 when a breaking change is detected.",
    )
    return parser


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(
            f"invalid JSON in {path}: line {exc.lineno}, column {exc.colno}"
        ) from exc


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = compare_payloads(
        load_json(args.baseline),
        load_json(args.candidate),
    )

    if args.output_format == "json":
        print(
            json.dumps(
                {
                    "breaking": result.has_breaking_changes,
                    "changes": [
                        {
                            **asdict(change),
                            "severity": change.severity.value,
                        }
                        for change in result.changes
                    ],
                },
                indent=2,
            )
        )
    else:
        _print_text(result)

    if args.fail_on_breaking and result.has_breaking_changes:
        return 2
    return 0


def _print_text(result) -> None:
    if not result.changes:
        print("No structural contract changes detected.")
        return

    print("API contract changes:")
    for change in result.changes:
        print(
            f"- [{change.severity.value.upper()}] "
            f"{change.path}: {change.message}"
        )

    breaking_count = len(result.breaking)
    print()
    print(
        f"{breaking_count} breaking change"
        f"{'' if breaking_count == 1 else 's'} detected."
    )


if __name__ == "__main__":
    raise SystemExit(main())
