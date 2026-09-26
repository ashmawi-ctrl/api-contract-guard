# API Contract Guard

A small CI-friendly tool for detecting breaking response-shape changes between a known-good API payload and a candidate payload.

The project is based on a production integration failure mode: the same response field can unexpectedly change from one data type to another, such as an object becoming a string. A downstream client may parse the documented shape correctly and still fail at runtime when the contract drifts.

The tool is intentionally focused on structural compatibility rather than business-value validation.

## Planned checks

- removed fields
- scalar/object/list type changes
- unexpected nullability
- nested object drift
- list item shape drift
- additive fields reported separately from breaking changes
- machine-readable exit codes for CI

The implementation is developed through issues and reviewable pull requests.
