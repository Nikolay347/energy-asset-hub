# ADR-007 — Preserve valid measurements when engineering validation reports issues

- **Status:** Accepted
- **Date:** 2026-10-

## Context

A telemetry packet can be structurally valid and produce legitimate normalized measurements while still representing an operating condition that violates engineering limits or cross-parameter rules.

Discarding those measurements would erase evidence of the abnormal operating condition that the engineering layer is intended to detect.

## Decision

When structural processing succeeds, persist the resulting `Measurement` objects even if engineering validation reports issues.

Engineering findings are stored separately in `BessEngineeringValidationOutcome` rather than being used to suppress the measurements.

## Consequences

- Abnormal but valid telemetry remains available for history, diagnostics, reporting, and future analytics.
- Engineering issues describe the operating state instead of rewriting the raw/normalized data history.
- Structural validity and operational acceptability remain independently traceable.
- Consumers must consider engineering outcomes when deciding whether a measurement is acceptable for a particular operational use.

## Related components

- `Measurement`
- `BessEngineeringValidationOutcome`
- `BessPacketProcessingService`
- `SQLiteMeasurementRepository`
- `SQLiteBessEngineeringValidationOutcomeRepository`
