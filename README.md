# Energy Asset Hub

Energy Asset Hub is a Python-based software project for collecting, validating, processing, 
analyzing, and storing operational telemetry from energy equipment.

The project focuses on Battery Energy Storage Systems (BESS), solar power installations, 
and other energy assets. It is designed to work with real operational parameters such as 
battery state of charge (SOC), electrical power, temperature, and other measurements received from 
external equipment.

The long-term objective is to build an extensible software system that can:
* Acquire operational data from equipment APIs, external services, and databases.
* Validate incoming data and convert it into consistent internal representations.
* Maintain historical records of equipment operating conditions.
* Analyze equipment performance and detect abnormal operating conditions.
* Support operational monitoring, diagnostics, and reporting.
* Provide a foundation for future predictive analytics and equipment control.

The architecture is intended to support multiple equipment types, independent data sources, 
and redundant communication channels.

Energy Asset Hub is being developed incrementally as an engineering-oriented Python portfolio project.
Its current implementation covers BESS telemetry validation, timestamp normalization, and the initial 
telemetry processing pipeline.

## Project Goals

The main goal of Energy Asset Hub is to provide a modular architecture for working with operational 
data from different types of energy assets.

The project is designed to support:

* Integration with different telemetry data sources and communication interfaces.
* Validation of incoming measurements and payloads.
* Transformation of external data into internal domain models.
* Consistent handling of timestamps across different time zones.
* Processing and analysis of operational parameters.
* Storage and retrieval of historical measurements.
* Monitoring, diagnostics, and reporting.
* Extension with device control capabilities.
* Support for redundant communication channels.

The functionality is being implemented incrementally.


## Current Implementation

### BESS Payload Validation

BessTelemetryPayloadValidator validates incoming telemetry payloads.

The current validation includes:

* Checking required fields.
* Checking field types.
* Rejecting boolean values where numeric values are expected.
* Checking state-of-charge (SOC) boundaries.
* Validating timestamp format.
* Collecting multiple validation issues in a single pass.

Validation results contain structured diagnostic information, including issue codes,
severity, affected fields, actual values, and expected values.

### Timestamp Normalization

TimestampNormalizer converts timestamps into timezone-aware UTC datetime objects.

Supported functionality includes:

* Converting timestamps containing explicit UTC offsets.
* Interpreting local timestamps using a configured source timezone.
* Detecting missing timezone information.
* Rejecting ambiguous local timestamps during daylight saving time transitions.
* Rejecting nonexistent local timestamps during daylight saving time transitions.

The source timezone can be supplied by the application when the external device 
does not include timezone information in its telemetry.

### BESS Telemetry Processing

BessTelemetryProcessor coordinates payload validation and timestamp normalization.

It:

* Validates incoming telemetry before normalization.
* Returns structured validation results.
* Produces a normalized UTC timestamp for successfully processed payloads.
* Converts supported timestamp normalization exceptions into validation issues.
* Avoids further processing when required validation fails.

The current processor operates on supplied Python dictionaries. Communication with 
real BESS devices is not yet implemented.

### Measurement Domain Model

`Measurement` is a reusable domain model representing a single
operational parameter of an energy asset.

Each measurement contains:

- Asset and data source identifiers.
- Parameter name, numerical value, and measurement unit.
- A timezone-aware UTC timestamp.

The model enforces basic data integrity:

- Only integer and floating-point values are accepted.
- Boolean values, NaN, and infinities are rejected.
- Timestamps must have a zero UTC offset.

Equipment-specific physical validation is planned separately.

### Timezone Database Check

TimezoneDatabaseCheck provides a basic diagnostic check for the availability of selected 
IANA timezone definitions, currently including UTC, Europe/Kyiv, and Europe/Warsaw.

This check is a supporting utility. It does not currently block telemetry processing or 
establish clock synchronization with external devices.


## Project Structure

The Python package is organized into domain and integration layers.

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
        └── telemetry_processor.py

The domain package contains reusable domain logic, validation structures, and time-related utilities.

The integrations package contains components specific to external data formats and integrations.


## Installation

The project is currently developed with Python 3.12.

Create and activate a virtual environment, then install the project dependencies:

python -m pip install -r requirements.txt

Install pytest to run the automated tests:

python -m pip install pytest

The tzdata dependency provides IANA timezone data, which is particularly useful on environments where 
a system timezone database is not available.


## Testing

The project uses pytest and follows an incremental test-driven development approach.

Tests cover:

* BESS payload validation.
* Timestamp normalization and timezone-related edge cases.
* BESS telemetry processing and error propagation.
* Basic timezone database availability.

Run all tests:

python -m pytest -v

Run only BESS telemetry processor tests:

python -m pytest tests/integrations/bess_api/test_telemetry_processor.py -v


## Planned Development

The next development stages include:

1. Transforming validated BESS telemetry into internal measurements.
2. Preserving raw telemetry packets and their diagnostic results.
3. Supporting reprocessing of stored raw packets after correcting source configuration, without requesting 
4. the same telemetry again.
5. Implementing measurement history storage and retrieval.
6. Adding real communication interfaces for energy assets.
7. Supporting multiple data sources and redundant communication channels.
8. Extending the platform with analysis, reporting, and monitoring capabilities.

Clock synchronization checks and automated device control are not part of the current 
implementation. Their necessity will be evaluated during later development.

## Development Status

Energy Asset Hub is under development.

The current implementation focuses on input validation, timestamp handling, and the initial BESS telemetry 
processing pipeline.

It is not yet a complete data acquisition or device control system.
