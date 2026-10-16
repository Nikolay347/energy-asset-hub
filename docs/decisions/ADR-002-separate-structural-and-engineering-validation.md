# ADR-002 — Separate structural validation from engineering validation

- **Status:** Accepted
- **Date:** 2026-10-

## Context

Two different questions must be answered when processing BESS telemetry:

1. Can the incoming data be interpreted correctly?
2. Is the interpreted operating condition physically or operationally acceptable?

Mixing these concerns would make diagnostics less clear and would couple data-format checks to equipment-specific engineering rules.

## Decision

Keep structural/technical validation and engineering validation as separate stages.

Structural processing checks such things as required fields, types, timestamp handling, and normalization. Engineering validation runs only after valid measurements exist and evaluates operating conditions against resolved limits and SOC discharge rules.

```text
raw telemetry
    ↓
structural validation + timestamp normalization
    ↓
Measurement[]
    ↓
engineering validation
```

## Consequences

- A structurally invalid packet does not produce measurements.
- A structurally valid packet can produce measurements even if engineering validation later reports issues.
- Diagnostics clearly distinguish malformed/uninterpretable data from unacceptable operating conditions.
- Engineering rules can evolve independently of integration payload rules.

## Related components

- `BessTelemetryPayloadValidator`
- `TimestampNormalizer`
- `BessTelemetryProcessor`
- `BessEngineeringValidator`
- `BessEngineeringValidationService`
