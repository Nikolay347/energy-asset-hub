# Energy Asset Hub — System Map

This map uses the stable IDs from `class_catalog.md`.


## Production startup and REST ingress

```text
python -m energy_asset_hub.main
        │
        ▼
run_from_default_settings()
        │
        ▼
build_default_app_settings()
        │
        ▼
CFG-006 AppSettings
        │
        ▼
main(settings)
        │
        ├── opens SQLite connection
        │
        ├── builds configured/default BESS registries
        │
        ├── uses unavailable external repositories as
        │   production fallback implementations
        │
        ▼
build_bess_runtime()
        │
        ├── INT-014 BessRestTelemetryAdapter
        |    ├── INT-015 RequestsHttpClient
        |    ├── TIME-006 SystemUtcClock
        |    └── INT-016 UuidPacketIdGenerator
        │
        ├── BOOT-002 SQLiteRepositories
        │      ├── SQL-001 raw packet repository
        │      ├── SQL-002 processing-attempt repository
        │      ├── SQL-003 measurement repository
        │      └── SQL-004 engineering-validation outcome repository
        │
        ├── SVC-005 BessEngineeringValidationService
        │
        └── APP-001 BessPacketProcessingService
        │
        ▼
BOOT-001 BessRuntime
        │
        ▼
run_bess_once()
        │
        ├── telemetry_adapter.fetch_packet()
        │          │
        │          ▼
        │      HTTP GET
        │          │
        │          ▼
        │      DOM-001 IngressTelemetryPacket
        │
        └── packet_processing_service.process_packet(...)
                   │
                   ▼
              APP-001
        BessPacketProcessingService
                   │
                   ▼
          existing packet pipeline
```
main() is the production startup orchestrator. It prepares the runtime
configuration and registries, opens the SQLite connection, builds the BESS
runtime, starts one telemetry acquisition/processing cycle, and guarantees
that the SQLite connection is closed in a finally block.
```text
main(settings)
    │
    ├── opens SQLite connection
    │
    ├── loads default BESS limits and SOC rule
    │
    ├── creates default registries
    │
    ├── creates ConfiguredBessRegistry
    │
    ├── creates production fallback implementations
    │   of external repositories
    │
    ├── calls build_bess_runtime(...)
    │       ↓
    │   receives a fully assembled BessRuntime
    │
    ├── calls run_bess_once(...)
    │
    └── guarantees that the SQLite connection is closed
```
The REST adapter is responsible only for transport-level acquisition and
creation of IngressTelemetryPacket. Structural validation, timestamp
normalization, engineering validation, and persistence remain downstream
responsibilities of the existing processing pipeline.

The current default telemetry URL is a placeholder configuration value.
No physical BESS device or external BESS controller providing a REST
telemetry API is currently connected.

The next integration step is to run the production application against a
controlled local REST server that emulates such an external telemetry source.


## End-to-end packet pipeline

```text
External telemetry source
        │
        ▼
DOM-001  IngressTelemetryPacket
        │
        ▼
APP-001  BessPacketProcessingService
        │
        ├── 1. REP-001 / SQL-001
        │      Persist raw packet BEFORE processing
        │
        ├── 2. REP-003
        │      Read latest attempt number
        │
        ├── 3. INT-008 BessTelemetryProcessingService
        │        │
        │        ├── INT-004 BessTelemetryProcessor
        │        │      ├── INT-001 structural validation
        │        │      └── TIME-001 timestamp normalization
        │        │
        │        ├── INT-005 → DOM-002 ProcessingAttempt
        │        └── INT-006 → DOM-004 Measurement[]
        │
        ├── 4. SVC-005 BessEngineeringValidationService
        │        ├── SVC-001 resolve operating limits
        │        ├── SVC-003 resolve SOC discharge rule
        │        └── VAL-001 engineering validation
        │                 ↓
        │              DOM-013 EngineeringValidationOutcome
        │
        ├── 5. REP-003 / SQL-002 save ProcessingAttempt
        ├── 6. REP-004 / SQL-003 save Measurement[]
        └── 7. REP-005 / SQL-004 save EngineeringValidationOutcome
```

## Engineering-validation branch

```text
CFG-001 ConfiguredBessRegistry
       │
       ├───────────────┐
       ▼               ▼
SVC-001 Limits      SVC-003 SOC Rule
Resolver            Resolver
  │                   │
  ├─ REP-006 external ├─ REP-008 external
  ├─ CFG-002 default  ├─ CFG-004 default
  ▼                   ▼
DOM-007             DOM-010
Resolved limits     Resolved SOC rule
       \               /
        \             /
         ▼           ▼
         SVC-005 EngineeringValidationService
                      │
                      ▼
                  VAL-001
             EngineeringValidator
                      │
                      ▼
                  DOM-013
            EngineeringValidationOutcome
```

## Persistence traceability

```text
SQL-001 telemetry_packets
        packet_id
           │
           ▼
SQL-002 processing_attempts
        packet_id + attempt_number
           │
           ├──────────────► SQL-003 measurements
           │
           └──────────────► SQL-004 engineering_validation_outcomes
                                      │
                                      └── engineering validation issues
```

The intended invariant is that no downstream processing record exists without the parent traceability record that explains which raw packet and which processing attempt produced it.

## Test-double selection map

```text
What do I need from this dependency in this test?

Not relevant; constructor only
        └── NoOp

Need to inspect calls/arguments
        └── Recording

Need to assert call order
        └── EventRecording

Need state across several operations
        └── InMemory

Need real database behavior / keys / SQL
        └── SQLite
```

See the `TEST-*` section of `class_catalog.md` for the concrete helper classes currently present in the project.
