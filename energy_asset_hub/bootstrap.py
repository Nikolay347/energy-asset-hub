import sqlite3
from energy_asset_hub.integrations.bess_api.bess_rest_telemetry_adapter import (
    BessRestTelemetryAdapter,
)
from dataclasses import dataclass

from energy_asset_hub.infrastructure.persistence.sqlite.sqlite_bess_engineering_validation_outcome_repository import (
    SQLiteBessEngineeringValidationOutcomeRepository,
)
from energy_asset_hub.infrastructure.persistence.sqlite.sqlite_measurement_repository import (
    SQLiteMeasurementRepository,
)
from energy_asset_hub.infrastructure.persistence.sqlite.sqlite_processing_attempt_repository import (
    SQLiteProcessingAttemptRepository,
)
from energy_asset_hub.infrastructure.persistence.sqlite.sqlite_telemetry_packet_repository import (
    SQLiteTelemetryPacketRepository,
)
from energy_asset_hub.application.bess_packet_processing_service import (
    BessPacketProcessingService,
)
from energy_asset_hub.integrations.bess_api.processing_service import (
    BessTelemetryProcessingService,
)
from energy_asset_hub.domain.services.bess_engineering_validation_service import (
    BessEngineeringValidationService,
)
from energy_asset_hub.domain.services.bess_limits_resolver import (
    BessLimitsResolver,
)
from energy_asset_hub.domain.services.bess_soc_discharging_rule_resolver import (
    BessSOCDischargingRuleResolver,
)
from energy_asset_hub.domain.validation.bess_engineering_validator import (
    BessEngineeringValidator,
)
from energy_asset_hub.infrastructure.time.system_utc_clock import (
    SystemUtcClock,
)



def build_rest_telemetry_adapter(
    source_id: str,
    telemetry_url: str,
) -> BessRestTelemetryAdapter:
    return BessRestTelemetryAdapter(
        source_id=source_id,
        telemetry_url=telemetry_url,
        clock=SystemUtcClock(),
    )


@dataclass(frozen=True, slots=True)
class BessRuntime:
    telemetry_adapter: BessRestTelemetryAdapter
    packet_processing_service: BessPacketProcessingService


@dataclass(frozen=True, slots=True)
class SQLiteRepositories:
    packet_repository: SQLiteTelemetryPacketRepository
    attempt_repository: SQLiteProcessingAttemptRepository
    measurement_repository: SQLiteMeasurementRepository
    engineering_validation_outcome_repository: (
        SQLiteBessEngineeringValidationOutcomeRepository
    )


def build_sqlite_repositories(
    connection: sqlite3.Connection,
) -> SQLiteRepositories:
    return SQLiteRepositories(
        packet_repository=SQLiteTelemetryPacketRepository(connection),
        attempt_repository=SQLiteProcessingAttemptRepository(connection),
        measurement_repository=SQLiteMeasurementRepository(connection),
        engineering_validation_outcome_repository=(
            SQLiteBessEngineeringValidationOutcomeRepository(connection)
        ),
    )


def build_bess_packet_processing_service(
    repositories: SQLiteRepositories,
    engineering_validation_service,
) -> BessPacketProcessingService:
    return BessPacketProcessingService(
        attempt_repository=repositories.attempt_repository,
        measurement_repository=repositories.measurement_repository,
        processing_service=BessTelemetryProcessingService(),
        engineering_validation_service=engineering_validation_service,
        engineering_validation_outcome_repository=(
            repositories.engineering_validation_outcome_repository
        ),
        packet_repository=repositories.packet_repository,
    )


def build_bess_engineering_validation_service(
    configured_registry,
    default_limits_registry,
    external_limits_repository,
    default_soc_rule_registry,
    external_soc_rule_repository,
) -> BessEngineeringValidationService:
    limits_resolver = BessLimitsResolver(
        configured_registry=configured_registry,
        default_registry=default_limits_registry,
        external_repository=external_limits_repository,
    )

    soc_rule_resolver = BessSOCDischargingRuleResolver(
        configured_registry=configured_registry,
        default_registry=default_soc_rule_registry,
        external_repository=external_soc_rule_repository,
    )

    engineering_validator = BessEngineeringValidator()

    return BessEngineeringValidationService(
        limits_resolver=limits_resolver,
        soc_rule_resolver=soc_rule_resolver,
        validator=engineering_validator,
    )


def build_bess_runtime(
    source_id: str,
    telemetry_url: str,
    connection: sqlite3.Connection,
    configured_registry,
    default_limits_registry,
    external_limits_repository,
    default_soc_rule_registry,
    external_soc_rule_repository,
) -> BessRuntime:
    telemetry_adapter = build_rest_telemetry_adapter(
        source_id=source_id,
        telemetry_url=telemetry_url,
    )

    repositories = build_sqlite_repositories(
        connection=connection,
    )

    engineering_validation_service = (
        build_bess_engineering_validation_service(
            configured_registry=configured_registry,
            default_limits_registry=default_limits_registry,
            external_limits_repository=external_limits_repository,
            default_soc_rule_registry=default_soc_rule_registry,
            external_soc_rule_repository=external_soc_rule_repository,
        )
    )

    packet_processing_service = (
        build_bess_packet_processing_service(
            repositories=repositories,
            engineering_validation_service=engineering_validation_service,
        )
    )

    return BessRuntime(
        telemetry_adapter=telemetry_adapter,
        packet_processing_service=packet_processing_service,
    )


