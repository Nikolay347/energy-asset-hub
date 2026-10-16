# ADR-006 — Number processing attempts independently for each packet

- **Status:** Accepted
- **Date:** 2026-10-

## Context

The same stored raw packet may be processed more than once, for example after correcting timezone or configuration information. Each processing run must remain distinguishable while still belonging to the same packet.

A single global attempt counter would not express this relationship clearly.

## Decision

Identify a processing attempt by the composite identity:

```text
(packet_id, attempt_number)
```

Attempt numbers start at `1` for each packet and increment independently per `packet_id`.

`BessPacketProcessingService` queries the latest attempt number for the current packet and assigns the next number.

## Consequences

- Reprocessing history is naturally grouped under the raw packet.
- Different packets can both have attempt `1` without conflict.
- Measurements and engineering-validation outcomes can reference the exact processing attempt that produced them.
- SQLite persistence uses `(packet_id, attempt_number)` as the processing-attempt primary key and as a parent key for downstream records.

## Related components

- `ProcessingAttempt`
- `ProcessingAttemptRepository`
- `SQLiteProcessingAttemptRepository`
- `BessPacketProcessingService`
