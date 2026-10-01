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

Its current implementation covers BESS telemetry validation, timestamp normalization, 
immutable validated payload snapshots, and transformation of BESS telemetry into 
reusable measurement objects.

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

The functionality is being implemented incrementally.

## Current Implementation

### BESS Payload Validation

`BessTelemetryPayloadValidator` validates incoming telemetry payloads.

The current validation includes:

- Checking required fields.
- Checking field types.
- Rejecting boolean values where numeric values are expected.
- Checking state-of-charge (SOC) boundaries.
- Validating timestamp format.
- Collecting multiple validation issues in a single pass.

Validation results contain structured diagnostic information, including issue codes, 
severity, affected fields, actual values, and expected values.

### Timestamp Normalization

`TimestampNormalizer` converts timestamps into timezone-aware UTC datetime objects.

Supported functionality includes:

- Converting timestamps containing explicit UTC offsets.
- Interpreting local timestamps using a configured source timezone.
- Detecting missing timezone information.
- Rejecting ambiguous local timestamps during daylight saving time transitions.
- Rejecting nonexistent local timestamps during daylight saving time transitions.

The source timezone can be supplied by the application when the external device does not 
include timezone information in its telemetry.

For example, a BESS installed in Poland can use the configured `Europe/Warsaw` timezone 
if its timestamps represent Polish local time.

The timezone configuration must reflect the device's actual clock settings, not merely 
its geographical location.

### BESS Telemetry Processing

`BessTelemetryProcessor` coordinates payload validation and timestamp normalization.

It:

- Validates incoming telemetry before normalization.
- Returns structured validation results.
- Produces a normalized UTC timestamp for successfully processed payloads.
- Converts supported timestamp normalization exceptions into validation issues.
- Avoids further processing when required validation fails.
- Creates an immutable snapshot of successfully validated payload fields.

The processor returns a `BessTelemetryProcessingResult` containing:

- `validation_result` — structured validation and diagnostic information.
- `timestamp_utc` — the normalized UTC timestamp, or `None` if processing fails.
- `validated_payload` — a validated payload snapshot, or `None` if processing fails.

The current processor operates on supplied Python dictionaries. Communication with real 
BESS devices is not yet implemented.

### Validated BESS Payload

`ValidatedBessPayload` represents an immutable snapshot of the validated fields of 
a single BESS telemetry packet.

It contains:

- Asset identifier.
- Original timestamp string.
- Battery state of charge.
- Electrical power.
- Temperature.

The snapshot is created only after successful payload validation and timestamp normalization.

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

Equipment-specific physical and operational validation is planned separately.

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

## Project Structure

The Python package is organized into domain and integration layers.

```text
energy_asset_hub/
├── domain/
│   ├── models/
│   │   └── measurement.py
│   ├── time/
│   │   ├── timestamp_normalizer.py
│   │   └── timezone_database_check.py
│   └── validation/
│       ├── enums.py
│       ├── validation_issue.py
│       └── validation_result.py
└── integrations/
    └── bess_api/
        ├── payload_validator.py
        ├── telemetry_processor.py
        └── measurement_mapper.py
```

The `domain` package contains reusable domain models, validation structures, 
and time-related utilities.

The `integrations` package contains components specific to external data formats 
and integration workflows.

The architecture separates equipment-specific data processing from reusable domain
representations.

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

The project uses pytest and follows an incremental test-driven development approach.

Tests cover:

- BESS payload validation.
- Field type validation and SOC boundary conditions.
- Timestamp normalization and timezone-related edge cases.
- BESS telemetry processing and error propagation.
- Validated payload snapshot integrity.
- Measurement domain model validation.
- BESS measurement mapping.
- Basic timezone database availability.

The current test suite contains 38 passing test cases.

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

The next development stages include:

1. Preserving original telemetry packets, source identifiers, reception timestamps, 
and diagnostic results.
2. Supporting reprocessing of stored raw packets after correcting source configuration, 
without requesting the same telemetry again.
3. Establishing a reliable relationship between original telemetry packets and the 
measurements derived from them.
4. Implementing measurement history storage and retrieval.
5. Adding real communication interfaces for energy assets.
6. Supporting multiple data sources and redundant communication channels.
7. Implementing equipment-specific physical and operational validation.
8. Extending the platform with operational analysis, monitoring, reporting, and 
predictive maintenance capabilities.

### Raw Telemetry Preservation and Reprocessing

A planned requirement is to preserve incoming telemetry packets, including packets that 
cannot be successfully validated or normalized.

Each stored packet should retain sufficient information for diagnostics and reprocessing,
including:

- Original received data.
- Data source identifier.
- Reception timestamp (`received_at_utc`).
- Validation and processing diagnostics.

After correcting a source configuration, such as a missing timezone definition, the system
should be able to reprocess previously stored telemetry without requesting the same data 
from the equipment again.

The original reception timestamp must be preserved during reprocessing.

### Equipment-Specific Validation

Future validation components will consider physical and operational requirements for 
particular equipment types.

For BESS installations, these may include:

- Permitted charging and discharging conditions.
- Equipment-specific temperature limits.
- Power and available energy relationships.
- Consistency between related operational parameters.

These checks will be based on the specifications and operating constraints of the 
relevant equipment.

### Clock Synchronization and Equipment Control

Clock synchronization checks and automated device control are not part of the current 
implementation.

Their necessity will be evaluated during later development.

Diagnostic checks should not unnecessarily interrupt telemetry acquisition from otherwise 
operational equipment.

## Development Status

Energy Asset Hub is under active development.

The current implementation provides the initial BESS telemetry processing pipeline, 
from input validation and timestamp normalization to the creation of individual 
measurement objects.

The project does not yet implement live device communication, persistent measurement history,
raw telemetry storage, or equipment control.

The next development focus is preserving original telemetry packets and their reception 
metadata to support reliable historical processing and future reprocessing workflows.