# Energy Asset Hub

Energy Asset Hub is a Python-based software project for collecting, validating, 
processing, analyzing, and storing operational telemetry from energy equipment.

The project focuses on Battery Energy Storage Systems (BESS), solar power installations,
and other energy assets. It is designed to work with real operational parameters such 
as battery state of charge (SOC), electrical power, temperature, and other measurements
received from external equipment.

The long-term objective is to build an extensible software system that can:

- Acquire operational data from equipment APIs, external services, and databases.
- Validate incoming data and convert it into consistent internal representations.
- Maintain historical records of equipment operating conditions.
- Analyze equipment performance and detect abnormal operating conditions.
- Support operational monitoring, diagnostics, and reporting.
- Provide a foundation for future predictive analytics and equipment control.

The architecture is intended to support multiple equipment types, independent data sources,
and redundant communication channels.

Energy Asset Hub is being developed incrementally as an engineering-oriented Python 
portfolio project.

Its current implementation covers BESS telemetry validation, raw packet
preservation, structural validation, timestamp normalization, measurement creation,
engineering validation, processing auditability, and SQLite persistence.

## Project Goals

The main goal of Energy Asset Hub is to provide a modular architecture for working 
with operational data from different types of energy assets.

The project is designed to support:

- Integration with different telemetry data sources and communication interfaces.
- Validation of incoming measurements and payloads.
- Transformation of external data into internal domain models.
- Consistent handling of timestamps across different time zones.
- Processing and analysis of operational parameters.
- Storage and retrieval of historical measurements.
- Monitoring, diagnostics, and reporting.
- Extension with device control capabilities.
- Support for redundant communication channels.

The functionality is being implemented iteratively.

## Current Implementation

The current implementation provides an end-to-end BESS telemetry processing pipeline 
with REST-based telemetry acquisition, raw packet preservation, validation, timestamp 
normalization, measurement creation, engineering validation, audit information, and SQLite
persistence.

### REST Telemetry Acquisition

BessRestTelemetryAdapter acquires one telemetry payload from a configured REST endpoint
using HTTP GET.

The production transport stack includes:

- RequestsHttpClient for HTTP communication.
- SystemUtcClock for recording the UTC reception time.
- UuidPacketIdGenerator for generating internal packet identifiers.
- BessRestTelemetryAdapter for creating an IngressTelemetryPacket.

The REST adapter is responsible only for transport-level acquisition and creation of 
the raw ingress packet.

It does not perform structural validation, timestamp normalization, engineering validation,
or persistence.

The current default telemetry URL is a placeholder. For a compatible external
REST/JSON source, configure the endpoint and verify its payload contract,
authentication, and equipment-specific settings.

### Local Mock BESS Integration

The project includes a standalone local HTTP mock device in
`tools/mock_bess/server.py`. It serves a fixed sample BESS payload at
`GET /telemetry` and acts as an external telemetry source for the existing
`BessRestTelemetryAdapter`.

The production application has been run against this server over real HTTP,
with the resulting packet, processing attempt, measurements, and engineering
validation outcome persisted to SQLite.

The integration is covered by **five automated tests**: four focused mock-server
tests in `tests/tools/mock_bess/test_server.py` and the end-to-end mock
HTTP-to-SQLite integration test in
`tests/integrations/test_mock_bess_production_flow.py`.

The fixed sample (`power_kw = -120.0`) intentionally exceeds the default charge
power limit (100 kW), confirming that successful structural processing can
coexist with a recorded engineering validation issue.

#### Run the local mock integration

Start the mock device in one terminal:

```powershell
python -m tools.mock_bess.server
```

In a second terminal, run one production acquisition and processing cycle
using a local SQLite database:

```powershell
@'
from dataclasses import replace
from energy_asset_hub.config.app_settings import build_default_app_settings
from energy_asset_hub.main import main

settings = replace(
    build_default_app_settings(),
    telemetry_url="http://127.0.0.1:8000/telemetry",
    sqlite_path="mock_bess_run.db",
)
main(settings)
'@ | python -
```

The integration test starts its own isolated mock server automatically:

```powershell
python -m pytest tests/integrations/test_mock_bess_production_flow.py -v
```

### Raw Telemetry Preservation

IngressTelemetryPacket represents the original telemetry received from an external source.

Raw packets are persisted before processing, including packets that later fail validation or 
timestamp normalization.

Each packet preserves:

- Internal packet identifier.
- Source identifier.
- UTC reception timestamp.
- Original payload.

This allows the original telemetry to remain available for diagnostics, auditing, and future
reprocessing without requesting the same data from the equipment again.

### BESS Payload Validation

`BessTelemetryPayloadValidator` structurally validates incoming telemetry payloads.

The current validation includes:

- Checking required fields.
- Checking field types.
- Rejecting boolean values where numeric values are expected.
- Checking state-of-charge (SOC) boundaries.
- Validating timestamp format.
- Collecting multiple validation issues in a single pass.

Validation results contain structured diagnostic information, including issue codes, 
severity, affected field, actual values, and expected values.

### Timestamp Normalization

`TimestampNormalizer` converts telemetry timestamps into timezone-aware UTC datetime objects.

Supported functionality includes:

- Converting timestamps containing explicit UTC offsets.
- Interpreting local timestamps using a configured source timezone.
- Detecting missing timezone information.
- Rejecting ambiguous local timestamps during daylight saving time transitions.
- Rejecting nonexistent local timestamps during daylight saving time transitions.

The source timezone can be supplied by the application when the external telemetry source
does not include timezone information in its telemetry.

For example, a BESS installed in Poland can use the configured `Europe/Warsaw` timezone 
if its timestamps represent Polish local time.

The configured timezone must represent the actual clock configuration of the source, not merely 
the geographical location of the equipment.

### BESS Telemetry Processing

Telemetry processing is split into two levels.

`BessTelemetryProcessor` performs validation and timestamp normalization for
a supplied BESS telemetry dictionary.

It:

- Validates incoming telemetry before normalization.
- Returns structured validation results.
- Produces a normalized UTC timestamp for successfully processed payloads.
- Converts supported timestamp-normalization exceptions into validation issues.
- Avoids further processing when required validation fails.
- Creates an immutable ValidatedBessPayload snapshot after successful validation.

The processor returns a `BessTelemetryProcessingResult` containing:

- `validation_result` — structured validation and diagnostic information.
- `timestamp_utc` — the normalized UTC timestamp, or `None` if processing fails.
- `validated_payload` — a validated payload snapshot, or `None` if processing fails.

BessTelemetryProcessingService operates one level above the processor.

It accepts an IngressTelemetryPacket together with processing metadata and
coordinates:

- Calling BessTelemetryProcessor for payload validation and timestamp normalization.
- Creating a ProcessingAttempt describing the result of that processing execution.
- Mapping successfully validated telemetry into domain Measurement objects.

A failed processing attempt therefore still produces structured diagnostic and
audit information, while successful processing produces both a successful
ProcessingAttempt and reusable Measurement objects.

The original IngressTelemetryPacket is preserved separately by the
application-level BessPacketProcessingService, allowing the same raw packet
to be processed again later, for example after correcting source timezone
configuration.

### Validated BESS Payload

`ValidatedBessPayload` represents an immutable snapshot of the validated fields of 
a single BESS telemetry packet.

It contains:

- Asset identifier.
- Original timestamp string.
- Battery state of charge.
- Electrical power.
- Temperature.

`ValidatedBessPayload` is created only after successful payload validation and successful timestamp
normalization.

The normalized UTC timestamp is stored separately in `BessTelemetryProcessingResult`.

Subsequent modifications to the original input dictionary do not affect the validated values.

`ValidatedBessPayload` is not a separate validator and does not replace the original raw 
telemetry packet.

Its purpose is to preserve the relationship between validated parameter values and their 
processing result.

### BESS Measurement Mapping

`BessMeasurementMapper` transforms a successful `BessTelemetryProcessingResult` 
into individual `Measurement` domain objects.

Currently, one BESS telemetry packet produces three measurements:

| Parameter | Measurement unit |
|---|---|
| Battery state of charge (`soc_percent`) | % |
| Electrical power (`power_kw`) | kW |
| Temperature (`temperature_c`) | °C |

Each measurement contains the asset identifier, source identifier, parameter name, 
numerical value, measurement unit, and normalized UTC timestamp.

The mapper uses the immutable `ValidatedBessPayload` snapshot provided 
by `BessTelemetryProcessingResult`.

It does not accept the original input dictionary as a separate argument.

This design prevents the accidental combination of parameter values from one telemetry
packet with the timestamp of another packet through the mapper interface.

Invalid processing results are rejected.

### Measurement Domain Model

`Measurement` is a reusable domain model representing a single operational parameter 
of an energy asset.

Each measurement contains:

- Asset identifier.
- Data source identifier.
- Parameter name.
- Numerical value.
- Measurement unit.
- Timezone-aware UTC timestamp.

The model enforces basic data integrity:

- Only integer and floating-point values are accepted.
- Boolean values are rejected.
- NaN and positive or negative infinity are rejected.
- Timestamps must have a zero UTC offset.

These checks protect the consistency of the internal measurement representation 
regardless of the original data source.

Equipment-specific physical and operational validation is implemented
separately and does not belong to the generic `Measurement` invariants.

### Timezone Database Check

`TimezoneDatabaseCheck` provides a basic diagnostic check for the availability of 
selected IANA timezone definitions, currently including:

- `UTC`
- `Europe/Kyiv`
- `Europe/Warsaw`

This check is a supporting utility.

It does not currently block telemetry processing or establish clock synchronization with 
external devices.

A missing timezone definition should not automatically prevent unrelated telemetry 
sources from operating.

### Engineering Validation

Equipment-specific engineering validation is separated from generic structural
validation and from the generic `Measurement` invariants.

`BessEngineeringValidationService` resolves the effective engineering rules for
the asset and applies `BessEngineeringValidator` to the processed BESS
measurements.

The current architecture supports:

- Per-asset BESS operating limits.
- SOC-dependent discharging rules.
- Default fallback limits and rules.
- External asset-specific rule repositories.
- Resolution of effective rules for each asset.
- Recording which source and resolution reason were used for the effective rules.
- Preserving measurements even when engineering validation reports issues.

The limits resolver and SOC discharging-rule resolver first verify that the
asset is configured.

When an external asset-specific value is available, it is used.

When the external repository returns no value, or when the external repository
is unavailable, the configured per-asset defaults are used according to the
resolver logic.

The resulting engineering-validation outcome remains separate from the
measurements themselves. This allows measured data to be preserved even when
the operating state violates an engineering rule.

### SQLite Persistence

The production persistence layer uses SQLite repositories for:

- Raw ingress telemetry packets.
- Processing attempts.
- Measurements.
- BESS engineering-validation outcomes.

Raw `IngressTelemetryPacket` data is persisted before processing begins.

This preserves the original received payload even when later structural
validation or timestamp normalization fails.

Processing attempts are stored separately from the raw packet. The same packet
can therefore have multiple processing attempts, for example after correcting
the source timezone or other configuration.

Measurements created from successful processing are persisted independently.

Engineering-validation outcomes are also persisted separately, preserving both
the validation result and the provenance of the rules used for that validation.

Together, these records provide traceability between:
```text
IngressTelemetryPacket
        │
        ├── ProcessingAttempt #1
        ├── ProcessingAttempt #2
        │       │
        │       └── Measurement[]
        │
        └── ...
                │
                └── EngineeringValidationOutcome
```

### Application Orchestration

`BessPacketProcessingService` is the application-layer orchestrator for one
already-created `IngressTelemetryPacket`.

It coordinates the complete internal packet-processing pipeline:

1. Persist the raw IngressTelemetryPacket.
2. Determine the next processing-attempt number.
3. Perform structural validation and timestamp normalization through
   `BessTelemetryProcessingService`.
4. Persist the resulting `ProcessingAttempt`.
5. Persist successfully created `Measurement` objects.
6. Perform BESS engineering validation when measurements are available.
7. Persist the resulting engineering-validation outcome.

Transport-specific communication is intentionally outside
`BessPacketProcessingService`.

The service does not know whether the ingress packet was obtained through REST,
MQTT, OPC UA, or another future transport mechanism.

### Production Startup

Production startup and dependency construction are separated from telemetry processing logic.

energy_asset_hub/bootstrap.py serves as the composition root. It assembles the concrete 
production components and their dependencies, including:

* REST telemetry adapter.
* SQLite repositories.
* BESS engineering-validation services and rule resolvers.
* BessPacketProcessingService.
* BessRuntime.

BessRuntime holds the assembled components required for telemetry acquisition and processing. It does not implement business logic.

energy_asset_hub/main.py provides the production entry point.

The main(settings) function:

1. Opens the SQLite connection.
2. Loads the default BESS operating limits and SOC discharging rule.
3. Initializes the configured and default rule registries.
4. Prepares fallback implementations for unavailable external rule repositories.
5. Calls build_bess_runtime(...) to assemble the production runtime.
6. Invokes run_bess_once(...) to execute one telemetry acquisition and processing cycle.
7. Closes the SQLite connection in a finally block.

run_bess_once(...) obtains an IngressTelemetryPacket through the configured telemetry 
adapter and passes it to BessPacketProcessingService.

The application can be started with:

python -m energy_asset_hub.main

The default telemetry URL is a placeholder and must be configured to point to an accessible 
telemetry source. Instructions for running against the local Mock BESS server are provided in the Local Mock BESS Integration section.

## Project Structure

The project is organized into application, domain, integration, infrastructure,
configuration, and startup/composition layers.

```text
energy_asset_hub/
├── application/
│   └── bess_packet_processing_service.py
│
├── config/
│   ├── app_settings.py
│   └── bess_defaults.py
│
├── domain/
│   ├── configuration/
│   │   ├── configured_bess_registry.py
│   │   ├── default_bess_limits_registry.py
│   │   └── default_bess_soc_discharging_rule_registry.py
│   │
│   ├── models/
│   │   ├── bess_engineering_validation_outcome.py
│   │   ├── bess_operating_limits.py
│   │   ├── bess_soc_discharging_rule.py
│   │   ├── ingress_telemetry_packet.py
│   │   ├── measurement.py
│   │   ├── processing_attempt.py
│   │   ├── resolved_bess_limits.py
│   │   └── resolved_bess_soc_discharging_rule.py
│   │
│   ├── repositories/
│   │   ├── bess_engineering_validation_outcome_repository.py
│   │   ├── external_bess_limits_repository.py
│   │   ├── external_bess_soc_discharging_rule_repository.py
│   │   ├── ingress_telemetry_packet_repository.py
│   │   ├── measurement_repository.py
│   │   └── processing_attempt_repository.py
│   │
│   ├── services/
│   │   ├── bess_engineering_validation_service.py
│   │   ├── bess_limits_resolver.py
│   │   └── bess_soc_discharging_rule_resolver.py
│   │
│   ├── time/
│   │   ├── timestamp_normalizer.py
│   │   └── timezone_database_check.py
│   │
│   └── validation/
│       ├── bess_engineering_validator.py
│       ├── enums.py
│       ├── validation_issue.py
│       └── validation_result.py
│
├── infrastructure/
│   ├── external/
│   │   ├── unavailable_bess_limits_repository.py
│   │   └── unavailable_bess_soc_discharging_rule_repository.py
│   │
│   ├── persistence/
│   │   └── sqlite/
│   │       ├── sqlite_bess_engineering_validation_outcome_repository.py
│   │       ├── sqlite_measurement_repository.py
│   │       ├── sqlite_processing_attempt_repository.py
│   │       └── sqlite_telemetry_packet_repository.py
│   │
│   └── time/
│       └── system_utc_clock.py
│
├── integrations/
│   ├── telemetry_adapter.py
│   │
│   └── bess_api/
│       ├── bess_rest_telemetry_adapter.py
│       ├── measurement_mapper.py
│       ├── payload_validator.py
│       ├── processing_attempt_mapper.py
│       ├── processing_service.py
│       ├── requests_http_client.py
│       ├── telemetry_processor.py
│       └── uuid_packet_id_generator.py
│
├── bootstrap.py
└── main.py

tools/
└── mock_bess/
    ├── __init__.py
    └── server.py
```

### Application Layer

The `application` package contains use-case orchestration.

`BessPacketProcessingService` coordinates the complete processing of one
already-created ingress telemetry packet, including persistence, processing,
measurement creation, engineering validation, and persistence of the resulting
outcome.

It depends on repository contracts and domain/integration services rather than
on concrete transport or persistence implementations.

### Configuration Layer

The `config` package contains startup configuration values and factories.

`AppSettings` defines runtime-specific settings such as:

- Asset identifier.
- Telemetry source identifier.
- REST telemetry URL.
- Source timezone.
- SQLite database path.

`bess_defaults.py` contains the current default BESS operating limits,
SOC discharging rule, and helpers for constructing the corresponding
per-asset default registries.

### Domain Layer

The `domain` package contains reusable business models, rules, repository
contracts, validation logic, and time-related domain utilities.

#### `domain/configuration`

Contains registries describing:

- Which BESS assets are configured.
- Default operating limits per asset.
- Default SOC-dependent discharging rules per asset.

#### `domain/models`

Contains domain models representing:

- Raw ingress telemetry packets.
- Measurements.
- Processing attempts.
- BESS operating limits.
- SOC-dependent discharging rules.
- Resolved rule sets and their provenance.
- Engineering-validation outcomes.

#### `domain/repositories`

Contains repository contracts used by higher-level services.

These contracts separate business and application logic from concrete storage
or external-source implementations.

#### `domain/services`

Contains domain services responsible for:

- Resolving effective BESS operating limits.
- Resolving effective SOC discharging rules.
- Coordinating BESS engineering validation.

#### `domain/time`

Contains timestamp normalization and timezone-database diagnostic utilities.

#### `domain/validation`

Contains generic validation structures and BESS-specific engineering validation
rules.

### Integration Layer

The `integrations` package contains components responsible for adapting external
telemetry data to the internal processing model.

`TelemetryAdapter` defines the current telemetry acquisition protocol.

The `bess_api` package contains the BESS REST integration and processing
components, including:

- REST telemetry acquisition.
- HTTP-client abstraction and production implementation.
- Internal packet-ID generation.
- BESS payload validation.
- Timestamp-aware telemetry processing.
- Mapping processing results to `ProcessingAttempt`.
- Mapping validated BESS data to `Measurement` objects.

Transport acquisition remains separated from application-layer packet
processing.

### Infrastructure Layer

The `infrastructure` package contains concrete technical implementations of
domain and integration contracts.

#### `infrastructure/persistence/sqlite`

Contains SQLite implementations for persistence of:

- Raw ingress telemetry packets.
- Processing attempts.
- Measurements.
- Engineering-validation outcomes.

#### `infrastructure/external`

Contains the current production fallback implementations representing
unavailable external sources of asset-specific engineering limits and rules.

These implementations allow the resolver logic to fall back to configured
per-asset defaults without changing the domain services.

#### `infrastructure/time`

Contains `SystemUtcClock`, the production implementation used to obtain the
current timezone-aware UTC time.

### Composition Root

`bootstrap.py` is the composition root.

It constructs and connects concrete production dependencies, including:

- REST telemetry adapter.
- SQLite repositories.
- Engineering-validation resolvers and services.
- `BessPacketProcessingService`.
- `BessRuntime`.

It performs dependency wiring only and does not implement business-processing
logic.

### Production Entry Point

See [Production Startup](#production-startup) for entry-point responsibilities,
configuration, and an example run against the local mock device.

## Tests and Architecture Documentation

The project also contains:
```text
tests/
├── application/
├── config/
├── domain/
├── infrastructure/
├── integrations/
│   └── test_mock_bess_production_flow.py
├── tools/
│   └── mock_bess/
│       └── test_server.py
├── test_bootstrap.py
└── test_main.py

docs/
├── architecture/
│   ├── class_catalog.md
│   └── system_map.md
└── decisions/
    ├── ADR-001-persist-raw-packet-before-processing.md
    ├── ADR-002-separate-structural-and-engineering-validation.md
    ├── ADR-003-use-repository-contracts-for-persistence-boundaries.md
    ├── ADR-004-use-default-fallback-rules-when-external-rules-are-unavailable.md
    ├── ADR-005-record-rule-provenance-in-engineering-outcomes.md
    ├── ADR-006-number-processing-attempts-per-packet.md
    ├── ADR-007-preserve-measurements-when-engineering-validation-reports-issues.md
    └── ADR-008-use-application-service-as-pipeline-orchestrator.md
```
The test suite mirrors the main architectural layers and includes both focused
component tests and integration tests covering the REST-to-SQLite processing
flow.

The architecture documentation provides:

- class_catalog.md — stable identifiers and responsibilities of important
  classes and protocols.
- system_map.md — end-to-end relationships and data flow between the main
  architectural components.
- ADR files — architectural decisions and their rationale.

## Installation

The project is currently developed with Python 3.12.

### Create a virtual environment

```powershell
python -m venv .venv
```

Activate the environment on Windows using PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Install project dependencies

```powershell
python -m pip install -r requirements.txt
```

The `tzdata` dependency provides IANA timezone data, which is particularly useful 
in environments where a system timezone database is not available.

### Install testing tools

```powershell
python -m pip install pytest
```

## Testing

The project uses `pytest` for unit, integration, persistence, and startup-wiring tests.

The current test suite covers:

- Domain model invariants.
- Structural telemetry validation.
- Timestamp normalization.
- Timezone handling and timezone-database checks.
- Immutable validated BESS payload snapshots.
- BESS telemetry processing.
- Processing-attempt creation.
- Reprocessing of preserved packets.
- Measurement mapping.
- Engineering validation.
- Engineering-rule resolution.
- Default fallback behavior when external engineering-rule sources are missing
  or unavailable.
- Rule-source and resolution-reason provenance.
- Raw ingress packet persistence.
- Processing-attempt persistence.
- Measurement persistence.
- Engineering-validation outcome persistence.
- SQLite repository behavior.
- REST telemetry acquisition.
- HTTP client behavior.
- Packet ID generation.
- Production UTC clock behavior.
- Bootstrap/composition-root wiring.
- Production startup flow.
- SQLite connection cleanup.
- REST-to-SQLite integration flow with a real local mock HTTP server.

The most recent full local test run completed with **200 passing tests** (`python -m pytest -q`).

Focused test groups can also be run independently.
For example:
```shell
python -m pytest tests/test_main.py -v

python -m pytest tests/integrations -v

python -m pytest tests/infrastructure -v
```

`python -m pytest` runs pytest through the currently active Python
interpreter, which helps ensure that the test suite uses the project's active
virtual environment.
The `-v` option enables verbose output.
The `-q` option enables compact output

### Run all tests

```powershell
python -m pytest -v
```

For a shorter test report:

```powershell
python -m pytest -q
```

### Run individual test modules

BESS telemetry processor:

```powershell
python -m pytest tests/integrations/bess_api/test_telemetry_processor.py -v
```

BESS measurement mapper:

```powershell
python -m pytest tests/integrations/bess_api/test_measurement_mapper.py -v
```

Measurement domain model:

```powershell
python -m pytest tests/domain/models/test_measurement.py -v
```

## Planned Development

The core BESS telemetry processing pipeline is already implemented.

Current and planned development is focused on extending production integration,
scalability, and operational capabilities.

### Near-Term Integration Work

The local mock REST-to-SQLite integration is implemented and covered by
automated tests. Remaining integration work includes:


- Replace the placeholder telemetry URL with a deployment-specific value loaded
  from an external configuration source.
- Add configuration loading from environment variables or another external
  configuration mechanism.
- Connect to a real BESS controller or external telemetry source when such an
  interface is available.

### Transport Expansion

The current production transport is REST request/response.

Future transport work may include:

- MQTT subscription-based telemetry.
- OPC UA industrial telemetry.
- SQL-based telemetry sources.
- Redundant communication channels.

Before adding MQTT or OPC UA, the current `TelemetryAdapter` contract should be
reviewed because subscription/stream-based transports have different runtime
behavior from REST request/response.

All transport implementations should continue producing the same internal
`IngressTelemetryPacket` boundary where practical.

### External Engineering Configuration

The current system supports default per-asset engineering rules and repository
contracts for external asset-specific rules.

Future work may include concrete implementations for:

- File-based engineering configuration.
- SQL-backed engineering configuration.
- REST-based engineering-rule services.
- Dynamic asset-specific limits.

The existing resolver and validation pipeline should remain unchanged when
these concrete repositories are added.

### Persistence and History

SQLite persistence is currently implemented.

Future persistence work may include:

- Richer historical queries.
- Operational reporting.
- Retention policies.
- Migration support.
- Additional database backends.

### Operational Processing

Future runtime capabilities may include:

- Continuous or scheduled telemetry polling.
- Multiple BESS assets.
- Multiple telemetry sources per asset.
- Source-health monitoring.
- Retry policies.
- Communication-failure handling.
- Stale-data detection.
- Redundant-source selection.

### Engineering Analysis

Future engineering-validation capabilities may include:

- Additional cross-parameter consistency rules.
- Power-versus-available-energy checks.
- More detailed temperature-dependent limits.
- Charge/discharge regime validation.
- Equipment-specific constraints from real manufacturer data.

### Analytics and Predictive Maintenance

Longer-term development may include:

- Historical trend analysis.
- Degradation indicators.
- Anomaly detection.
- Predictive maintenance.
- Machine-learning models based on accumulated operational data.

These capabilities should remain downstream of the validated and auditable
telemetry-processing pipeline rather than replacing the engineering and data
integrity layers.

## Development Approach

The project is developed incrementally using test-driven development (TDD).

The typical development cycle is:

```text
Red → Green → Refactor
```
This means:
1. Add or update a focused test describing the required behavior.
2. Run the test and confirm that it fails for the expected reason.
3. Implement the smallest meaningful production change needed to satisfy the
   test.
4. Run the focused test again.
5. Run the broader regression test suite.
6. Refactor only when behavior is already protected by tests.

Development is intentionally performed in small, reviewable steps.

The project favors:

- Clear separation of responsibilities.
- Small focused classes and services.
- Explicit dependency boundaries.
- Repository contracts between business logic and persistence.
- Separation of transport, application, domain, and infrastructure concerns.
- Reusable internal models independent of external transport mechanisms.
- Traceability of telemetry processing and engineering decisions.
- Production-like architecture without unnecessary abstraction.
- Tests that verify meaningful behavior rather than trivial object storage.

Large refactorings are avoided unless they solve a concrete architectural or
maintenance problem.

New components are introduced only when they have a clear responsibility in
the processing pipeline.

The current architecture is expected to evolve incrementally as new transports,
external rule sources, additional asset types, and operational capabilities are
added.

This project is being developed as a hands-on learning and portfolio project, using test-driven development 
and iterative architecture development.
AI-assisted development is used for code review, architecture discussions, learning, and exploring implementation 
alternatives. Design decisions and code changes are reviewed and verified as part of the development process.

## Development Status

The current working prototype processes one BESS telemetry packet per
production invocation and has been verified against a standalone local mock
HTTP source with SQLite persistence. See [Current Implementation](#current-implementation)
for implemented functionality, [Testing](#testing) for verification, and
[Planned Development](#planned-development) for future work.

The local mock is a fixed-response telemetry source, not yet a configurable
simulator or browser dashboard. Connection to a physical BESS has not been
tested; device-specific integration requires a compatible HTTP/JSON endpoint,
payload mapping, and configuration.


