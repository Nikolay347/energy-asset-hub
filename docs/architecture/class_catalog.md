# Energy Asset Hub — Class Catalog

> **Purpose.** Stable traceability catalog for classes in the current project snapshot. IDs are documentation 
identifiers only; Python class names and import paths remain the source-code identifiers.

## ID rules

- IDs are **stable**. Once assigned, an ID is not renumbered because rows move or new classes appear.
- A removed class leaves its ID reserved; do not reuse it for another class.
- Prefixes identify architectural area:
  - `APP` — application orchestration
  - `BOOT` — composition root / runtime assembly containers
  - `DOM` — domain models and enums
  - `REP` — repository contracts / repository-level support
  - `CFG` — domain configuration registries
  - `SVC` — domain services / resolvers
  - `VAL` — validation
  - `TIME` — time and timezone handling
  - `INT` — BESS API integration / mapping / processing
  - `SQL` — SQLite persistence implementations
  - `TEST` — test doubles and test-only helper classes
  - `SIM` — local equipment simulation tools
- Status legend: `✅ active`, `🟡 partial / future extension expected`, `🧪 test-only`.

## Application

| ID | Class | Path | Responsibility | Depends on / collaborates with | Main output / side effect | Status |
|---|---|---|---|---|---|---|
| APP-001 | `BessPacketProcessingService` | `energy_asset_hub/application/bess_packet_processing_service.py` | Orchest<br/>rates one packet through the end-to-end application pipeline. Persists raw packet before processing, assigns attempt number, invokes telemetry processing and engineering validation, then persists results. | `REP-001`, `REP-003`, `REP-004`, `REP-005`, `INT-008`, `SVC-005` | Saved raw packet, `ProcessingAttempt`, `Measurement[]`, optional `BessEngineeringValidationOutcome`; returns processing result | ✅ |

## Composition root / runtime assembly

| ID | Class | Path | Responsibility | Contains / collaborates with | Status |
|---|---|---|---|---|---|
| BOOT-001 | `BessRuntime` | `energy_asset_hub/bootstrap.py` | Runtime container for the top-level BESS components required to acquire and process telemetry. It does not implement processing logic itself. | `INT-014`, `APP-001` | ✅ |
| BOOT-002 | `SQLiteRepositories` | `energy_asset_hub/bootstrap.py` | Groups the concrete SQLite repository implementations created from one SQLite connection and passed into application-service construction. | `SQL-001`, `SQL-002`, `SQL-003`, `SQL-004` | ✅ |

## Domain models and enums

| ID | Class | Path | Responsibility | Main users | Status |
|---|---|---|---|---|---|
| DOM-001 | `IngressTelemetryPacket` | `domain/models/ingress_telemetry_packet.py` | Immutable/raw ingress snapshot: packet identity, source, original payload, receive time. | `APP-001`, `INT-008`, `REP-001`, `SQL-001` | ✅ |
| DOM-002 | `ProcessingAttempt` | `domain/models/processing_attempt.py` | Audit record for one processing attempt of one packet. | `INT-005`, `REP-003`, `SQL-002`, `APP-001` | ✅ |
| DOM-003 | `ProcessingStatus` | `domain/models/processing_attempt.py` | Enum describing processing outcome/status. | `DOM-002`, `INT-005`, `SQL-002` | ✅ |
| DOM-004 | `Measurement` | `domain/models/measurement.py` | Normalized measurement with traceability to packet/attempt. | `INT-006`, `REP-004`, `SQL-003`, `APP-001` | ✅ |
| DOM-005 | `BessOperatingLimits` | `domain/models/bess_operating_limits.py` | Engineering operating limits for a BESS asset. | `CFG-002`, `SVC-001`, `VAL-001`, `DOM-007` | ✅ |
| DOM-006 | `BessSOCDischargingRule` | `domain/models/bess_soc_discharging_rule.py` | SOC-dependent discharge rule; calculates allowed discharge fraction. | `CFG-004`, `SVC-003`, `VAL-001`, `DOM-010` | ✅ |
| DOM-007 | `ResolvedBessLimits` | `domain/models/resolved_bess_limits.py` | Effective limits plus provenance/source and resolution reason. | `SVC-001`, `SVC-005`, `DOM-013`, `SQL-004` | ✅ |
| DOM-008 | `BessLimitsSource` | `domain/models/resolved_bess_limits.py` | Enum identifying where effective limits came from. | `SVC-001`, `DOM-007`, `SQL-004` | ✅ |
| DOM-009 | `BessLimitsResolutionReason` | `domain/models/resolved_bess_limits.py` | Enum explaining why a limits source was selected. | `SVC-001`, `DOM-007`, `SQL-004` | ✅ |
| DOM-010 | `ResolvedBessSOCDischargingRule` | `domain/models/resolved_bess_soc_discharging_rule.py` | Effective SOC discharge rule plus provenance and resolution reason. | `SVC-003`, `SVC-005`, `DOM-013`, `SQL-004` | ✅ |
| DOM-011 | `BessSOCDischargingRuleSource` | `domain/models/resolved_bess_soc_discharging_rule.py` | Enum identifying SOC-rule source. | `SVC-003`, `DOM-010`, `SQL-004` | ✅ |
| DOM-012 | `BessSOCDischargingRuleResolutionReason` | `domain/models/resolved_bess_soc_discharging_rule.py` | Enum explaining SOC-rule resolution choice. | `SVC-003`, `DOM-010`, `SQL-004` | ✅ |
| DOM-013 | `BessEngineeringValidationOutcome` | `domain/models/bess_engineering_validation_outcome.py` | Audit-ready engineering-validation result combining validation issues and exact resolved rule/limit provenance. | `SVC-005`, `REP-005`, `SQL-004`, `APP-001` | ✅ |

## Repository contracts and repository support

| ID | Class | Path | Responsibility | Implemented / used by | Status |
|---|---|---|---|---|---|
| REP-001 | `IngressTelemetryPacketRepository` | `domain/repositories/ingress_telemetry_packet_repository.py` | Contract for saving/querying raw ingress packets. | `REP-002`, `SQL-001`, injected into `APP-001` | ✅ |
| REP-002 | `InMemoryIngressTelemetryPacketRepository` | same file as `REP-001` | In-memory implementation of raw packet repository for non-SQL scenarios/tests. | Repository tests / development flows | ✅ |
| REP-003 | `ProcessingAttemptRepository` | `domain/repositories/processing_attempt_repository.py` | Contract for saving/getting attempts and finding latest attempt number per packet. | `SQL-002`, injected into `APP-001` | ✅ |
| REP-004 | `MeasurementRepository` | `domain/repositories/measurement_repository.py` | Contract for persisting measurements. | `SQL-003`, injected into `APP-001` | ✅ |
| REP-005 | `BessEngineeringValidationOutcomeRepository` | `domain/repositories/bess_engineering_validation_outcome_repository.py` | Contract for persisting engineering-validation outcome for packet + attempt. | `SQL-004`, injected into `APP-001` | ✅ |
| REP-006 | `ExternalBessLimitsRepository` | `domain/repositories/external_bess_limits_repository.py` | Contract for optional external/asset-specific operating limits. | Used by `SVC-001` | 🟡 |
| REP-007 | `ExternalBessLimitsRepositoryUnavailableError` | same file as `REP-006` | Signals external limits source is temporarily unavailable. | Handled by `SVC-001` | ✅ |
| REP-008 | `ExternalBessSOCDischargingRuleRepository` | `domain/repositories/external_bess_soc_discharging_rule_repository.py` | Contract for optional external/asset-specific SOC discharge rule. | Used by `SVC-003` | 🟡 |
| REP-009 | `ExternalBessSOCDischargingRuleRepositoryUnavailableError` | same file as `REP-008` | Signals external SOC-rule source is unavailable. | Handled by `SVC-003` | ✅ |
| REP-010 | `UnavailableBessLimitsRepository` | `infrastructure/external/unavailable_bess_limits_repository.py` | Production fallback implementation representing an unavailable external source of asset-specific BESS operating limits. Raises the repository-unavailable error when queried. | Implements the role of `REP-006`; used by `SVC-001` through bootstrap/main wiring | ✅ |
| REP-011 | `UnavailableBessSOCDischargingRuleRepository` | `infrastructure/external/unavailable_bess_soc_discharging_rule_repository.py` | Production fallback implementation representing an unavailable external source of asset-specific SOC discharging rules. Raises the repository-unavailable error when queried. | Implements the role of `REP-008`; used by `SVC-003` through bootstrap/main wiring | ✅ |

## Domain configuration registries

| ID | Class | Path | Responsibility | Main users | Status |
|---|---|---|---|---|---|
| CFG-001 | `ConfiguredBessRegistry` | `domain/configuration/configured_bess_registry.py` | Knows whether a BESS asset is configured/known. | `SVC-001`, `SVC-003` | ✅ |
| CFG-002 | `DefaultBessLimitsRegistry` | `domain/configuration/default_bess_limits_registry.py` | Provides per-asset default/fallback `BessOperatingLimits`. | `SVC-001` | ✅ |
| CFG-003 | `BessDefaultLimitsNotFoundError` | same file as `CFG-002` | Signals missing default limits for requested asset. | Registry/resolver flow | ✅ |
| CFG-004 | `DefaultBessSOCDischargingRuleRegistry` | `domain/configuration/default_bess_soc_discharging_rule_registry.py` | Provides default/fallback SOC discharge rule per asset. | `SVC-003` | ✅ |
| CFG-005 | `BessDefaultSOCDischargingRuleNotFoundError` | same file as `CFG-004` | Signals missing default SOC discharge rule. | Registry/resolver flow | ✅ |
| CFG-006 | AppSettings | config/app_settings.py | Immutable startup configuration containing asset identity, telemetry source, REST URL, source timezone and SQLite database path. | main() / production startup | ✅ |
| CFG-007 | BessDefaultRegistries | config/bess_defaults.py | Groups the per-asset default limits registry and default SOC discharging-rule registry created for startup configuration. | CFG-002, CFG-004, main() | ✅ |

## Domain services / engineering resolution

| ID | Class | Path | Responsibility | Depends on | Output | Status |
|---|---|---|---|---|---|---|
| SVC-001 | `BessLimitsResolver` | `domain/services/bess_limits_resolver.py` | Resolves effective BESS limits from configured asset, external repository and defaults, preserving reason/source. | `CFG-001`, `CFG-002`, `REP-006` | `DOM-007` | ✅ |
| SVC-002 | `UnknownConfiguredBessError` | same file as `SVC-001` | Signals that requested asset is not in configured registry. | `SVC-001` flow | — | ✅ |
| SVC-003 | `BessSOCDischargingRuleResolver` | `domain/services/bess_soc_discharging_rule_resolver.py` | Resolves effective SOC discharge rule with provenance/reason. | `CFG-001`, `CFG-004`, `REP-008` | `DOM-010` | ✅ |
| SVC-004 | `UnknownConfiguredBessSOCDischargingRuleError` | same file as `SVC-003` | Signals SOC-rule resolution for unknown/unconfigured asset. | `SVC-003` flow | — | ✅ |
| SVC-005 | `BessEngineeringValidationService` | `domain/services/bess_engineering_validation_service.py` | Coordinates effective-limit resolution, SOC-rule resolution and engineering validation for one operating point. | `SVC-001`, `SVC-003`, `VAL-001` | `DOM-013` | ✅ |

## Validation

| ID | Class | Path | Responsibility | Main users | Status |
|---|---|---|---|---|---|
| VAL-001 | `BessEngineeringValidator` | `domain/validation/bess_engineering_validator.py` | Applies engineering/physical operating-condition rules (temperature, SOC, charge/discharge power, SOC-dependent discharge). | `SVC-005` | ✅ |
| VAL-002 | `ValidationResult` | `domain/validation/validation_result.py` | Aggregates validation issues; exposes validity and warning checks. | Structural and engineering validation flows | ✅ |
| VAL-003 | `ValidationIssue` | `domain/validation/validation_issue.py` | One structured diagnostic issue with field/code/severity/message/actual/expected. | `VAL-002`, processing attempts, SQLite persistence | ✅ |
| VAL-004 | `IssueSeverity` | `domain/validation/enums.py` | Severity enum for diagnostics. | Validators, persistence | ✅ |
| VAL-005 | `ValidationIssueCode` | `domain/validation/enums.py` | Stable issue-code enum. | Validators, processing, persistence | ✅ |

## Time and timezone handling

| ID | Class | Path | Responsibility | Main users | Status |
|---|---|---|---|---|---|
| TIME-001 | `TimestampNormalizer` | `domain/time/timestamp_normalizer.py` | Converts raw timestamps to UTC; handles source timezone and DST edge cases. | `INT-004` | ✅ |
| TIME-002 | `TimezoneRequiredError` | same file as `TIME-001` | Signals that timezone is required to interpret naive local timestamp. | `INT-004` handles it | ✅ |
| TIME-003 | `AmbiguousLocalTimeError` | same file as `TIME-001` | Signals DST-fold ambiguous local time. | `INT-004` handles it | ✅ |
| TIME-004 | `NonexistentLocalTimeError` | same file as `TIME-001` | Signals local wall-clock time that does not exist due to timezone transition. | `INT-004` handles it | ✅ |
| TIME-005 | `TimezoneDatabaseCheck` | `domain/time/timezone_database_check.py` | Checks availability of timezone database support. | Startup/environment validation tests | ✅ |
| TIME-006 | `SystemUtcClock` | `infrastructure/time/system_utc_clock.py` | Production UTC clock returning the current timezone-aware system time. Used for transport receipt time and startup processing time. | REST adapter construction; `main()` / `run_bess_once()` | ✅ |

## BESS API integration and mapping

| ID | Class | Path | Responsibility | Depends on | Output | Status |
|--|---|---|---|---|---|---|
| INT-001 | `BessTelemetryPayloadValidator` | `integrations/bess_api/payload_validator.py` | Structural/schema-level validation of incoming BESS payload fields/types/basic ranges. | `VAL-002`/`VAL-003`/enums | `ValidationResult` | ✅ |
| INT-002 | `ValidatedBessPayload` | `integrations/bess_api/telemetry_processor.py` | Typed validated payload snapshot used after structural validation/timestamp normalization. | `INT-004` | Internal processing value | ✅ |
| INT-003 | `BessTelemetryProcessingResult` | same file as `INT-002` | Result of low-level BESS telemetry processing, including validation/normalized data. | `INT-004`, `INT-005`, `INT-006` | Internal processing result | ✅ |
| INT-004 | `BessTelemetryProcessor` | `integrations/bess_api/telemetry_processor.py` | Coordinates structural validation and timestamp normalization. | `INT-001`, `TIME-001`, validation types | `INT-003` | ✅ |
| INT-005 | `BessProcessingAttemptMapper` | `integrations/bess_api/processing_attempt_mapper.py` | Maps processing result into auditable `ProcessingAttempt`. | `INT-003`, `DOM-002` | `DOM-002` | ✅ |
| INT-006 | `BessMeasurementMapper` | `integrations/bess_api/measurement_mapper.py` | Maps successful normalized BESS processing result into traceable measurements. | `INT-003`, `DOM-004` | `list[Measurement]` | ✅ |
| INT-007 | `BessTelemetryProcessingServiceResult` | `integrations/bess_api/processing_service.py` | Bundles `ProcessingAttempt` and generated measurements returned to application orchestration. | `INT-008` | Attempt + measurements | ✅ |
| INT-008 | `BessTelemetryProcessingService` | `integrations/bess_api/processing_service.py` | Coordinates processor + attempt mapper + measurement mapper for one packet and attempt number. | `INT-004`, `INT-005`, `INT-006` | `INT-007` | ✅ |
| INT-009 | `TelemetryAdapter` | `integrations/telemetry_adapter.py` | Transport-facing protocol defining the current ingress contract: obtain one `IngressTelemetryPacket`. Intended as the common boundary for telemetry acquisition implementations. | Implemented structurally by `INT-014`; consumed by runtime/startup architecture | `DOM-001` | 🟡 |
| INT-010 | `HttpResponse` | `integrations/bess_api/bess_rest_telemetry_adapter.py` | Protocol describing the minimal HTTP response behavior required by the REST telemetry adapter: status checking and JSON decoding. | `INT-014`, HTTP client implementation | HTTP response abstraction | ✅ |
| INT-011 | `HttpClient` | `integrations/bess_api/bess_rest_telemetry_adapter.py` | Protocol describing the minimal HTTP client capability required by the REST adapter. | `INT-014`; production implementation `INT-015` | `INT-010` | ✅ |
| INT-012 | `Clock` | `integrations/bess_api/bess_rest_telemetry_adapter.py` | Protocol supplying the UTC receipt timestamp without coupling the REST adapter to the system clock implementation. | `INT-014`; production implementation `TIME-006` | timezone-aware UTC `datetime` | ✅ |
| INT-013 | `PacketIdGenerator` | `integrations/bess_api/bess_rest_telemetry_adapter.py` | Protocol for generating an internal packet identifier independently of transport payload contents. | `INT-014`; production implementation `INT-016` | packet ID string | ✅ |
| INT-014 | `BessRestTelemetryAdapter` | `integrations/bess_api/bess_rest_telemetry_adapter.py` | Acquires one BESS telemetry payload via HTTP GET, verifies HTTP success, records receipt time, generates a packet ID and creates the raw `IngressTelemetryPacket`. It does not perform structural or engineering validation. | `INT-011`, `INT-012`, `INT-013`, `DOM-001` | `DOM-001` | ✅ |
| INT-015 | `RequestsHttpClient` | `integrations/bess_api/requests_http_client.py` | Production HTTP-client implementation backed by `requests.Session`; performs GET requests with a configured timeout. | Implements `INT-011`; used by `INT-014` | HTTP response | ✅ |
| INT-016 | `UuidPacketIdGenerator` | `integrations/bess_api/uuid_packet_id_generator.py` | Production packet-ID generator using UUID version 4 for internally generated ingress packet identifiers. | Implements `INT-013`; used by `INT-014` | packet ID string | ✅ |


## Local BESS simulation tools

The local Mock BESS server emulates an external HTTP telemetry source for integration testing and end-to-end demonstrations.
The simulator is independent of the production telemetry-processing pipeline. It communicates with the platform through the existing REST telemetry adapter, allowing the simulated equipment to be replaced with a compatible real telemetry source without changing the core processing logic.

| ID | Class | Path | Responsibility | Main collaborators | Status |
|---|---|---|---|---|---|
| SIM-001 | `BessRequestHandler` | `tools/mock_bess/server.py` | Handles HTTP GET requests, returns JSON telemetry at `/telemetry`, and responds with HTTP 404 for unsupported routes. | `BaseHTTPRequestHandler`, `HTTPServer` | Implemented |

### Server startup

The `run_server()` function in `tools/mock_bess/server.py` initializes the local HTTP server, starts request handling through `serve_forever()`, and ensures that the server socket is closed during shutdown.

### Integration testing

The simulator is covered by four tests in `tests/tools/mock_bess/test_server.py`.
An additional end-to-end integration test, `tests/integrations/test_mock_bess_production_flow.py`, verifies the complete execution path:
`Mock BESS → HTTP GET → REST Adapter → Packet Processing → Engineering Validation → SQLite`
The test confirms persistence of the incoming telemetry packet, processing attempt, normalized measurements, and engineering-validation issues.

## SQLite infrastructure

| ID | Class | Path | Responsibility | Domain contract / model | Key integrity relation | Status |
|---|---|---|---|---|---|---|
| SQL-001 | `SQLiteTelemetryPacketRepository` | `infrastructure/persistence/sqlite/sqlite_telemetry_packet_repository.py` | SQLite implementation for raw packet persistence and queries. | `REP-001`, `DOM-001` | Root record for downstream packet traceability | ✅ |
| SQL-002 | `SQLiteProcessingAttemptRepository` | `infrastructure/persistence/sqlite/sqlite_processing_attempt_repository.py` | Persists attempt and diagnostics; retrieves attempts/latest number. | `REP-003`, `DOM-002` | `(packet_id, attempt_number)` linked to raw packet | ✅ |
| SQL-003 | `SQLiteMeasurementRepository` | `infrastructure/persistence/sqlite/sqlite_measurement_repository.py` | Persists/retrieves individual measurements. | `REP-004`, `DOM-004` | Composite FK to processing attempt | ✅ |
| SQL-004 | `SQLiteBessEngineeringValidationOutcomeRepository` | `infrastructure/persistence/sqlite/sqlite_bess_engineering_validation_outcome_repository.py` | Persists/restores engineering outcome, resolved limits/rule provenance and validation issues. | `REP-005`, `DOM-013` | Composite FK to processing attempt; issues linked to outcome | ✅ |

## Test-only helper classes

These classes are deliberately **not part of the production pipeline**. Their purpose is to isolate behavior under test.

| ID | Class | Test file | Type / purpose | Use when |
|---|---|---|---|---|
| TEST-001 | `NoOpMeasurementRepository` | `tests/application/test_bess_packet_processing_service.py` | No-op | Measurement persistence is irrelevant to the current test |
| TEST-002 | `NoOpTelemetryPacketRepository` | same | No-op | Raw packet persistence is not the subject of the test |
| TEST-003 | `RecordingProcessingAttemptRepository` | same | Recording/stub | Need controlled latest-attempt number and/or to inspect saved attempts |
| TEST-004 | `NoOpBessEngineeringValidationService` | same | No-op service | Engineering validation is irrelevant to the test |
| TEST-005 | `NoOpEngineeringValidationOutcomeRepository` | same | No-op | Outcome persistence is irrelevant |
| TEST-006 | `RecordingTelemetryPacketRepository` | same | Recording | Need to verify which raw packets were saved |
| TEST-007 | `InMemoryProcessingAttemptRepository` | same | In-memory stateful repository | Need real attempt-number behavior across several calls |
| TEST-008 | `RecordingMeasurementRepository` | same | Recording | Need to inspect saved measurements |
| TEST-009 | `RecordingEngineeringValidationService` | same | Recording service | Need to inspect engineering-validation calls / return controlled outcome |
| TEST-010 | `EventRecordingMeasurementRepository` | same | Event recorder | Need ordering assertions involving measurement persistence |
| TEST-011 | `EventRecordingEngineeringValidationService` | same | Event recorder | Need ordering assertions involving engineering validation |
| TEST-012 | `RecordingEngineeringValidationOutcomeRepository` | same | Recording | Need to verify outcome persistence arguments |
| TEST-013 | `EventRecordingTelemetryPacketRepository` | same | Event recorder | Need to verify raw packet save occurs before later steps |
| TEST-014 | `EventRecordingProcessingService` | same | Event recorder + real-service wrapper | Need to mark `processing_started` while retaining real processing behavior |
| TEST-015 | `StubBessLimitsResolver` | `tests/domain/services/test_bess_engineering_validation_service.py` | Stub | Supply controlled resolved limits |
| TEST-016 | `StubBessSOCDischargingRuleResolver` | same | Stub | Supply controlled resolved SOC rule |
| TEST-017 | `FakeExternalBessLimitsRepository` | `tests/domain/services/test_bess_limits_resolver.py` | Fake | Simulate available external limits source |
| TEST-018 | `UnavailableExternalBessLimitsRepository` | same | Failure fake | Simulate unavailable external limits source |
| TEST-019 | `FakeExternalBessSOCDischargingRuleRepository` | `tests/domain/services/test_bess_soc_discharging_rule_resolver.py` | Fake | Simulate available external SOC-rule source |
| TEST-020 | `UnavailableExternalBessSOCDischargingRuleRepository` | same | Failure fake | Simulate unavailable external SOC-rule source |
| TEST-021 | `FakeExternalBessLimitsRepository` | `tests/domain/repositories/test_external_bess_limits_repository.py` | Contract fake | Exercises repository contract shape in repository-level test |
| TEST-022 | `FakeExternalBessSOCDischargingRuleRepository` | `tests/domain/repositories/test_external_bess_soc_discharging_rule_repository.py` | Contract fake | Exercises SOC-rule repository contract shape |
| TEST-023 | `NoOpBessEngineeringValidationService` | `tests/application/test_bess_packet_processing_service_sqlite.py` | No-op service | SQLite application tests where engineering validation is not under test |
| TEST-024 | `NoOpEngineeringValidationOutcomeRepository` | same | No-op | SQLite application tests where outcome persistence is not under test |

## How to use this catalog during development

Before adding or changing a component, answer four questions:

1. **Where is it on the system map?**
2. **Which stable ID does it have (or which new ID should be assigned)?**
3. **What does it depend on, and who depends on it?**
4. **Which tests prove its contract and its place in the pipeline?**

When a class changes responsibility, update this catalog in the same branch/commit as the code change. 
When a new class is introduced, assign the next unused ID in its prefix group; never renumber existing IDs.


