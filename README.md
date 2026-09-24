# Energy Asset Hub

Energy Asset Hub is a Python project for collecting, validating, processing, analyzing, and
storing telemetry data from energy assets.

The project is designed to support further extension with historical data management, monitoring,
reporting, and device control capabilities.

It is developed as a learning and portfolio project focused on software engineering practices for
industrial and energy-related systems.

## Project Goals

The main goal of Energy Asset Hub is to provide a modular architecture for working with operational 
data from different types of energy assets.

The project is being designed to support:

* integration with different telemetry data sources;
* validation of incoming measurements and payloads;
* transformation of external data into internal domain models;
* processing and analysis of operational parameters;
* storage and retrieval of historical measurements;
* generation of reports and operational summaries;
* extension with monitoring, diagnostics, and control-related functionality;
* support for multiple asset types and communication interfaces.

## Current Project Structure

The current project structure separates domain logic from external integrations.

energy_asset_hub/
├── domain/
│   ├── models/
│   └── validation/
└── integrations/
    └── bess_api/

The domain package contains core business entities and validation logic.

The integrations package contains components responsible for communication with external systems and
data sources.

The bess_api package is currently used for integration-related logic associated with Battery Energy 
Storage System telemetry.