# ADR-003 — Use repository contracts at persistence boundaries

- **Status:** Accepted
- **Date:** 2026-10-

## Context

Application and domain logic should not depend directly on SQLite-specific SQL operations. 
The project is intended to remain extensible to other persistence technologies and to support lightweight test doubles.

## Decision

Define repository contracts with Python `Protocol` classes and inject repository implementations into 
higher-level services.

SQLite implementations live in the infrastructure layer, while application/domain code depends on 
repository behavior rather than SQL details.

Examples include:

- `IngressTelemetryPacketRepository`
- `ProcessingAttemptRepository`
- `MeasurementRepository`
- `BessEngineeringValidationOutcomeRepository`

## Consequences

- SQLite can be replaced or complemented without rewriting the orchestration logic.
- Unit tests can use `NoOp`, `Recording`, `EventRecording`, or in-memory implementations.
- Persistence responsibilities remain separated from business and engineering logic.
- Repository contracts must be kept aligned with the capabilities required by their callers.

## Related components

- `BessPacketProcessingService`
- `SQLiteTelemetryPacketRepository`
- `SQLiteProcessingAttemptRepository`
- `SQLiteMeasurementRepository`
- `SQLiteBessEngineeringValidationOutcomeRepository`
