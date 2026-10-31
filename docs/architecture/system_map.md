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
build_default_app_settings() → CFG-006 AppSettings
        │
        ▼
main(settings)
        ├── opens SQLite connection
        ├── builds default BESS limits and SOC-rule registries
        ├── creates ConfiguredBessRegistry
        ├── provides unavailable external repository implementations
        │   (fallback to configured defaults)
        │
        ▼
build_bess_runtime()                [bootstrap.py: composition root]
        ├── INT-014 BessRestTelemetryAdapter
        │   ├── INT-015 RequestsHttpClient
        │   ├── TIME-006 SystemUtcClock
        │   └── INT-016 UuidPacketIdGenerator
        ├── BOOT-002 SQLiteRepositories
        │   ├── SQL-001 raw packet repository
        │   ├── SQL-002 processing-attempt repository
        │   ├── SQL-003 measurement repository
        │   └── SQL-004 engineering-validation outcome repository
        ├── SVC-005 BessEngineeringValidationService
        └── APP-001 BessPacketProcessingService
        │
        ▼
BOOT-001 BessRuntime
        │
        ▼
run_bess_once()                      [main.py: one acquisition cycle]
        │
        ├── telemetry_adapter.fetch_packet()
        │       │
        │       ├── HTTP GET /telemetry ──► Local Mock BESS
        │       │                          tools/mock_bess/server.py
        │       │                          (separate HTTP server)
        │       │       ◄── JSON payload ──┘
        │       ▼
        │   DOM-001 IngressTelemetryPacket
        │
        └── packet_processing_service.process_packet(...)
                │
                ▼
             APP-001 BessPacketProcessingService
                │
                ▼
             End-to-end packet pipeline (below)

main(settings) closes the SQLite connection in a finally block.
```

The mock BESS and the production application run as independent components.
The REST adapter initiates HTTP requests (pull model); the mock server responds
with telemetry. The same adapter can target another compatible HTTP/JSON source
through configuration. Integration with physical equipment remains device-specific
and has not been demonstrated by the local mock test.

The REST adapter handles transport acquisition and construction of
`IngressTelemetryPacket`. Structural validation, timestamp normalization,
engineering checks and persistence remain in the downstream pipeline.

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

## Local mock BESS integration verification

- `tools/mock_bess/server.py` implements `GET /telemetry` with a fixed JSON payload
  and returns HTTP 404 for unknown paths.
- `tests/tools/mock_bess/test_server.py` checks the standalone HTTP server behavior.
- `tests/integrations/test_mock_bess_production_flow.py` uses a local HTTP server
  on an ephemeral port and a temporary SQLite database. It verifies persisted
  ingress, a successful processing attempt, measurements, and an engineering
  limit violation recorded separately from processing diagnostics.
- The simulator is currently fixed-payload; browser control, configurable
  simulation scenarios and a browser-facing read API are future work.

