# ADR-008 — Use an application service as the packet-processing orchestrator

- **Status:** Accepted
- **Date:** 2026-10-

## Context

The end-to-end packet flow spans several responsibilities: raw persistence, attempt numbering, telemetry processing, engineering validation, and persistence of multiple outputs.

Placing all of that logic inside a validator, processor, mapper, or repository would create an oversized component and blur layer boundaries.

## Decision

Use `BessPacketProcessingService` as the application-level orchestrator for one packet-processing workflow.

It coordinates dependencies and ordering but delegates specialized work:

- raw persistence to a packet repository;
- structural processing to `BessTelemetryProcessingService`;
- engineering validation to `BessEngineeringValidationService`;
- persistence to the corresponding repositories.

Specialized components remain responsible for their own focused behavior.

## Consequences

- The complete workflow is visible in one application-level service.
- Validators, mappers, resolvers, and repositories remain focused and reusable.
- Ordering requirements can be tested explicitly, including "persist raw packet before processing".
- The orchestrator gains dependencies as the workflow grows, so constructor size and responsibility boundaries should be reviewed periodically.

## Related components

- `BessPacketProcessingService`
- `BessTelemetryProcessingService`
- `BessEngineeringValidationService`
- repository contracts
