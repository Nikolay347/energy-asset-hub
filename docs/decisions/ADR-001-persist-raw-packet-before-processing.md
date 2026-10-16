# ADR-001 — Persist raw telemetry packet before processing

- **Status:** Accepted
- **Date:** 2026-10-

## Context

A telemetry packet may later fail structural validation, timestamp normalization, or another processing step. If the original input is not persisted first, the system can lose the exact data that arrived from the source.

The project also needs to support later reprocessing after configuration changes, such as correcting a source timezone.

## Decision

Persist every `IngressTelemetryPacket` before starting processing.

`BessPacketProcessingService.process_packet()` calls the raw-packet repository first and only then determines the processing-attempt number and invokes `BessTelemetryProcessingService`.

```text
IngressTelemetryPacket
        ↓
persist raw packet
        ↓
processing
```

## Consequences

- Invalid or unprocessable packets are still retained.
- Reprocessing can use the original packet without requesting it again from the device.
- Downstream records can be traced back to a stored raw packet.
- Packet identifiers must behave as stable identities; saving the same ID with different content is rejected by the current repositories.

## Related components

- `IngressTelemetryPacket`
- `IngressTelemetryPacketRepository`
- `SQLiteTelemetryPacketRepository`
- `BessPacketProcessingService`
