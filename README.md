# API Contract Guard

[![quality](https://github.com/ashmawi-ctrl/api-contract-guard/actions/workflows/quality.yml/badge.svg)](https://github.com/ashmawi-ctrl/api-contract-guard/actions/workflows/quality.yml)

A CI-friendly command-line tool for detecting breaking structural drift between a known-good JSON API response and a candidate response.

This project is built around a production integration failure mode: a client can correctly implement the documented response contract and still fail if the same field unexpectedly changes type at runtime.

For example, a bilingual object:

```json
{
  "transactionResponseMessage": {
    "en": "Settled",
    "ar": "تم التسوية"
  }
}
```

becoming:

```json
{
  "transactionResponseMessage": "Settled"
}
```

is a breaking structural change for clients expecting an object.

## What it checks

- removed fields
- nested field drift
- object / string / number / boolean / array changes
- non-null values becoming null
- representative list item shape changes
- candidate arrays that become empty
- additive fields, reported as informational changes
- CI exit status for breaking drift

## Install

Python 3.11+:

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -e ".[dev]"
```

## Compare two payloads

```bash
api-contract-guard examples/baseline.json examples/candidate.json
```

Example output:

```text
API contract changes:
- [INFO] $.trace_id: new field added to candidate payload
- [BREAKING] $.history[0].transactionResponseMessage: type changed from object to string

1 breaking change detected.
```

The command exits with status `2` when breaking drift exists, making it suitable for CI.

## JSON output

```bash
api-contract-guard \
  examples/baseline.json \
  examples/candidate.json \
  --format json
```

Example shape:

```json
{
  "breaking": true,
  "changes": [
    {
      "path": "$.history[0].transactionResponseMessage",
      "severity": "breaking",
      "kind": "type_changed",
      "message": "type changed from object to string"
    }
  ]
}
```

## Do not fail CI

For exploratory comparisons:

```bash
api-contract-guard baseline.json candidate.json --no-fail-on-breaking
```

## Run locally

```bash
make install
make quality
make example
```

## Docker

```bash
docker build -t api-contract-guard .

docker run --rm \
  -v "$PWD/examples:/data:ro" \
  api-contract-guard \
  /data/baseline.json \
  /data/candidate.json
```

## Design decisions

### Structural compatibility, not business correctness

The tool answers questions like:

> Did this response field disappear or change type?

It does not decide whether a status code, amount, or business state is logically correct.

### Added fields are not treated as breaking

Adding a new response field is normally backward compatible for tolerant clients, so additions are reported with `info` severity.

### Arrays use a representative item

The current version compares the first item in non-empty arrays. This keeps the tool deterministic and simple for response examples, but it is not a replacement for a full JSON Schema validator.

### Empty candidate arrays are warnings

If the baseline contains an item but the candidate array is empty, the tool cannot verify the candidate item shape. That produces a warning rather than guessing.

## Project structure

```text
contract_guard/
  cli.py       command-line interface and exit codes
  compare.py   recursive structural comparison
  models.py    result and severity models

tests/
  test_cli.py
  test_compare.py

examples/
  baseline.json
  candidate.json
```

## Engineering workflow

The first recursive comparison implementation is tracked through:

- [Issue #1](https://github.com/ashmawi-ctrl/api-contract-guard/issues/1)
- feature branch: `feat/recursive-contract-diff`
- regression tests
- CI checks
- reviewable pull request

## Current limitations

- compares JSON examples, not OpenAPI documents
- arrays are sampled using the first element
- does not yet support configurable ignored paths
- does not infer optional fields from multiple examples

## Next improvements

- compare OpenAPI response schemas
- optional / required field policy
- path ignore rules
- compare a set of captured examples instead of one payload
- SARIF or GitHub annotation output
- GitHub Action wrapper

## License

MIT
