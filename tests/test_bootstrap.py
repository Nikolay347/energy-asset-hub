from energy_asset_hub.bootstrap import build_rest_telemetry_adapter
from energy_asset_hub.integrations.bess_api.bess_rest_telemetry_adapter import (
    BessRestTelemetryAdapter,
)
import sqlite3

from energy_asset_hub.bootstrap import (
    BessRuntime,
    build_bess_runtime,
    build_bess_engineering_validation_service,
    build_bess_packet_processing_service,
    build_rest_telemetry_adapter,
    build_sqlite_repositories,
)
from energy_asset_hub.infrastructure.persistence.sqlite.sqlite_telemetry_packet_repository import (
    SQLiteTelemetryPacketRepository,
)
from energy_asset_hub.infrastructure.persistence.sqlite.sqlite_processing_attempt_repository import (
    SQLiteProcessingAttemptRepository,
)
from energy_asset_hub.infrastructure.persistence.sqlite.sqlite_measurement_repository import (
    SQLiteMeasurementRepository,
)
from energy_asset_hub.infrastructure.persistence.sqlite.sqlite_bess_engineering_validation_outcome_repository import (
    SQLiteBessEngineeringValidationOutcomeRepository,
)
from energy_asset_hub.application.bess_packet_processing_service import (
    BessPacketProcessingService,
)
from energy_asset_hub.domain.services.bess_engineering_validation_service import (
    BessEngineeringValidationService,
)
from energy_asset_hub.domain.configuration.configured_bess_registry import (
    ConfiguredBessRegistry,
)
from energy_asset_hub.domain.configuration.default_bess_limits_registry import (
    DefaultBessLimitsRegistry,
)
from energy_asset_hub.domain.configuration.default_bess_soc_discharging_rule_registry import (
    DefaultBessSOCDischargingRuleRegistry,
)
from energy_asset_hub.domain.models.bess_operating_limits import (
    BessOperatingLimits,
)
from energy_asset_hub.domain.models.bess_soc_discharging_rule import (
    BessSOCDischargingRule,
)
from energy_asset_hub.domain.models.resolved_bess_limits import (
    BessLimitsSource,
)
from energy_asset_hub.domain.models.resolved_bess_soc_discharging_rule import (
    BessSOCDischargingRuleSource,
)
from energy_asset_hub.infrastructure.time.system_utc_clock import (
    SystemUtcClock,
)



class FakeBessEngineeringValidationService:
    def validate_asset_operating_conditions(
        self,
        asset_id: str,
        temperature_c: float,
        soc_percent: float,
        power_kw: float,
    ):
        return None


def test_bootstrap_builds_rest_telemetry_adapter():
    adapter = build_rest_telemetry_adapter(
        source_id="BESS-01-REST",
        telemetry_url="http://bess-device/telemetry",
    )

    assert isinstance(adapter, BessRestTelemetryAdapter)
    assert isinstance(
        adapter._clock,
        SystemUtcClock,
    )


def test_bootstrap_builds_sqlite_repositories():
    connection = sqlite3.connect(":memory:")

    repositories = build_sqlite_repositories(connection)

    assert isinstance(
        repositories.packet_repository,
        SQLiteTelemetryPacketRepository,
    )
    assert isinstance(
        repositories.attempt_repository,
        SQLiteProcessingAttemptRepository,
    )
    assert isinstance(
        repositories.measurement_repository,
        SQLiteMeasurementRepository,
    )
    assert isinstance(
        repositories.engineering_validation_outcome_repository,
        SQLiteBessEngineeringValidationOutcomeRepository,
    )


def test_bootstrap_builds_bess_packet_processing_service():
    connection = sqlite3.connect(":memory:")

    repositories = build_sqlite_repositories(connection)

    engineering_validation_service = (
        FakeBessEngineeringValidationService()
    )

    service = build_bess_packet_processing_service(
        repositories=repositories,
        engineering_validation_service=engineering_validation_service,
    )

    assert isinstance(
        service,
        BessPacketProcessingService,
    )


class FakeExternalBessLimitsRepository:
    def get(
        self,
        asset_id: str,
    ):
        return None


class FakeExternalBessSOCDischargingRuleRepository:
    def get(
        self,
        asset_id: str,
    ):
        return None


def test_bootstrap_builds_bess_engineering_validation_service():
    default_limits = BessOperatingLimits(
        min_temperature_c=-20.0,
        max_temperature_c=55.0,
        min_soc_percent=10.0,
        max_soc_percent=95.0,
        max_charge_power_kw=100.0,
        max_discharge_power_kw=120.0,
    )

    default_soc_rule = BessSOCDischargingRule(
        full_power_soc_percent=20.0,
        reduced_power_soc_percent=10.0,
        reduced_power_fraction=0.5,
    )

    configured_registry = ConfiguredBessRegistry(
        asset_ids={"BESS-01"},
    )

    default_limits_registry = DefaultBessLimitsRegistry(
        limits_by_asset={
            "BESS-01": default_limits,
        }
    )

    default_soc_rule_registry = (
        DefaultBessSOCDischargingRuleRegistry(
            rules_by_asset={
                "BESS-01": default_soc_rule,
            }
        )
    )

    service = build_bess_engineering_validation_service(
        configured_registry=configured_registry,
        default_limits_registry=default_limits_registry,
        external_limits_repository=(
            FakeExternalBessLimitsRepository()
        ),
        default_soc_rule_registry=default_soc_rule_registry,
        external_soc_rule_repository=(
            FakeExternalBessSOCDischargingRuleRepository()
        ),
    )

    outcome = service.validate_asset_operating_conditions(
        asset_id="BESS-01",
        temperature_c=28.0,
        soc_percent=70.0,
        power_kw=50.0,
    )

    assert isinstance(
        service,
        BessEngineeringValidationService,
    )
    assert outcome.resolved_limits.source is BessLimitsSource.DEFAULT
    assert (
        outcome.resolved_soc_rule.source
        is BessSOCDischargingRuleSource.DEFAULT
    )
    assert outcome.validation_result.is_valid


def test_bootstrap_builds_bess_runtime():
    connection = sqlite3.connect(":memory:")

    default_limits = BessOperatingLimits(
        min_temperature_c=-20.0,
        max_temperature_c=55.0,
        min_soc_percent=10.0,
        max_soc_percent=95.0,
        max_charge_power_kw=100.0,
        max_discharge_power_kw=120.0,
    )

    default_soc_rule = BessSOCDischargingRule(
        full_power_soc_percent=20.0,
        reduced_power_soc_percent=10.0,
        reduced_power_fraction=0.5,
    )

    configured_registry = ConfiguredBessRegistry(
        asset_ids={"BESS-01"},
    )

    default_limits_registry = DefaultBessLimitsRegistry(
        limits_by_asset={
            "BESS-01": default_limits,
        }
    )

    default_soc_rule_registry = (
        DefaultBessSOCDischargingRuleRegistry(
            rules_by_asset={
                "BESS-01": default_soc_rule,
            }
        )
    )

    runtime = build_bess_runtime(
        source_id="BESS-01-REST",
        telemetry_url="http://bess-device/telemetry",
        connection=connection,
        configured_registry=configured_registry,
        default_limits_registry=default_limits_registry,
        external_limits_repository=(
            FakeExternalBessLimitsRepository()
        ),
        default_soc_rule_registry=default_soc_rule_registry,
        external_soc_rule_repository=(
            FakeExternalBessSOCDischargingRuleRepository()
        ),
    )

    assert isinstance(runtime, BessRuntime)
    assert isinstance(
        runtime.telemetry_adapter,
        BessRestTelemetryAdapter,
    )
    assert isinstance(
        runtime.packet_processing_service,
        BessPacketProcessingService,
    )

