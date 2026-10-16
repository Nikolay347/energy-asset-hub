import sqlite3
import pytest

from energy_asset_hub.domain.models.bess_engineering_validation_outcome import (
    BessEngineeringValidationOutcome,
)
from energy_asset_hub.domain.models.bess_operating_limits import (
    BessOperatingLimits,
)
from energy_asset_hub.domain.models.bess_soc_discharging_rule import (
    BessSOCDischargingRule,
)
from energy_asset_hub.domain.models.resolved_bess_limits import (
    BessLimitsResolutionReason,
    BessLimitsSource,
    ResolvedBessLimits,
)
from energy_asset_hub.domain.models.resolved_bess_soc_discharging_rule import (
    BessSOCDischargingRuleResolutionReason,
    BessSOCDischargingRuleSource,
    ResolvedBessSOCDischargingRule,
)
from energy_asset_hub.domain.validation.validation_result import (
    ValidationResult,
)
from energy_asset_hub.infrastructure.persistence.sqlite.sqlite_bess_engineering_validation_outcome_repository import (
    SQLiteBessEngineeringValidationOutcomeRepository,
)
from energy_asset_hub.domain.validation.enums import (
    IssueSeverity,
    ValidationIssueCode,
)
from energy_asset_hub.domain.validation.validation_issue import (
    ValidationIssue,
)
from datetime import datetime, timezone

from energy_asset_hub.domain.models.processing_attempt import (
    ProcessingAttempt,
    ProcessingStatus,
)
from energy_asset_hub.infrastructure.persistence.sqlite.sqlite_processing_attempt_repository import (
    SQLiteProcessingAttemptRepository,
)
from energy_asset_hub.domain.models.ingress_telemetry_packet import (
    IngressTelemetryPacket,
)
from energy_asset_hub.infrastructure.persistence.sqlite.sqlite_telemetry_packet_repository import (
    SQLiteTelemetryPacketRepository,
)


def test_save_and_get_engineering_validation_outcome():
    connection = sqlite3.connect(":memory:")

    repository = SQLiteBessEngineeringValidationOutcomeRepository(
        connection
    )

    limits = BessOperatingLimits(
        min_temperature_c=-20.0,
        max_temperature_c=55.0,
        min_soc_percent=10.0,
        max_soc_percent=95.0,
        max_charge_power_kw=100.0,
        max_discharge_power_kw=120.0,
    )

    resolved_limits = ResolvedBessLimits(
        limits=limits,
        source=BessLimitsSource.DEFAULT,
        reason=BessLimitsResolutionReason.EXTERNAL_NOT_FOUND,
    )

    soc_rule = BessSOCDischargingRule(
        full_power_soc_percent=20.0,
        reduced_power_soc_percent=10.0,
        reduced_power_fraction=0.5,
    )

    resolved_soc_rule = ResolvedBessSOCDischargingRule(
        rule=soc_rule,
        source=BessSOCDischargingRuleSource.DEFAULT,
        reason=BessSOCDischargingRuleResolutionReason.EXTERNAL_NOT_FOUND,
    )

    outcome = BessEngineeringValidationOutcome(
        validation_result=ValidationResult(),
        resolved_limits=resolved_limits,
        resolved_soc_rule=resolved_soc_rule,
    )

    repository.save(
        packet_id="PKT-0007",
        attempt_number=1,
        outcome=outcome,
    )

    restored_outcome = repository.get(
        packet_id="PKT-0007",
        attempt_number=1,
    )

    assert restored_outcome == outcome


def test_save_and_get_engineering_validation_outcome_preserves_issues():
    connection = sqlite3.connect(":memory:")

    repository = SQLiteBessEngineeringValidationOutcomeRepository(
        connection
    )

    limits = BessOperatingLimits(
        min_temperature_c=-20.0,
        max_temperature_c=55.0,
        min_soc_percent=10.0,
        max_soc_percent=95.0,
        max_charge_power_kw=100.0,
        max_discharge_power_kw=120.0,
    )

    resolved_limits = ResolvedBessLimits(
        limits=limits,
        source=BessLimitsSource.DEFAULT,
        reason=BessLimitsResolutionReason.EXTERNAL_NOT_FOUND,
    )

    soc_rule = BessSOCDischargingRule(
        full_power_soc_percent=20.0,
        reduced_power_soc_percent=10.0,
        reduced_power_fraction=0.5,
    )

    resolved_soc_rule = ResolvedBessSOCDischargingRule(
        rule=soc_rule,
        source=BessSOCDischargingRuleSource.DEFAULT,
        reason=BessSOCDischargingRuleResolutionReason.EXTERNAL_NOT_FOUND,
    )

    issue = ValidationIssue(
        field_name="temperature_c",
        code=ValidationIssueCode.VALUE_OUT_OF_RANGE,
        severity=IssueSeverity.ERROR,
        message="Temperature is above the allowed maximum",
        actual_value=70.0,
        expected="<= 55.0",
    )

    outcome = BessEngineeringValidationOutcome(
        validation_result=ValidationResult(
            issues=(issue,)
        ),
        resolved_limits=resolved_limits,
        resolved_soc_rule=resolved_soc_rule,
    )

    repository.save(
        packet_id="PKT-0007",
        attempt_number=1,
        outcome=outcome,
    )

    restored_outcome = repository.get(
        packet_id="PKT-0007",
        attempt_number=1,
    )

    assert restored_outcome == outcome


def test_save_engineering_validation_outcome_rejects_missing_processing_attempt():
    connection = sqlite3.connect(":memory:")
    connection.execute("PRAGMA foreign_keys = ON")

    from energy_asset_hub.infrastructure.persistence.sqlite.sqlite_processing_attempt_repository import (
        SQLiteProcessingAttemptRepository,
    )

    SQLiteProcessingAttemptRepository(connection)

    repository = SQLiteBessEngineeringValidationOutcomeRepository(
        connection
    )

    limits = BessOperatingLimits(
        min_temperature_c=-20.0,
        max_temperature_c=55.0,
        min_soc_percent=10.0,
        max_soc_percent=95.0,
        max_charge_power_kw=100.0,
        max_discharge_power_kw=120.0,
    )

    resolved_limits = ResolvedBessLimits(
        limits=limits,
        source=BessLimitsSource.DEFAULT,
        reason=BessLimitsResolutionReason.EXTERNAL_NOT_FOUND,
    )

    soc_rule = BessSOCDischargingRule(
        full_power_soc_percent=20.0,
        reduced_power_soc_percent=10.0,
        reduced_power_fraction=0.5,
    )

    resolved_soc_rule = ResolvedBessSOCDischargingRule(
        rule=soc_rule,
        source=BessSOCDischargingRuleSource.DEFAULT,
        reason=BessSOCDischargingRuleResolutionReason.EXTERNAL_NOT_FOUND,
    )

    outcome = BessEngineeringValidationOutcome(
        validation_result=ValidationResult(),
        resolved_limits=resolved_limits,
        resolved_soc_rule=resolved_soc_rule,
    )

    with pytest.raises(sqlite3.IntegrityError):
        repository.save(
            packet_id="PKT-0007",
            attempt_number=1,
            outcome=outcome,
        )


def test_save_engineering_validation_outcome_succeeds_when_processing_attempt_exists():
    connection = sqlite3.connect(":memory:")
    connection.execute("PRAGMA foreign_keys = ON")

    packet_repository = SQLiteTelemetryPacketRepository(
        connection
    )

    packet = IngressTelemetryPacket(
        packet_id="PKT-0007",
        source_id="BESS-01-API",
        ingress_payload={
            "asset_id": "BESS-01",
            "timestamp": "2026-10-02T12:30:00+03:00",
            "soc_percent": 72.5,
            "power_kw": -120.0,
            "temperature_c": 28.3,
        },
        received_at_utc=datetime(
            2026, 10, 2, 9, 30, 5,
            tzinfo=timezone.utc,
        ),
    )

    packet_repository.save(packet)

    attempt_repository = SQLiteProcessingAttemptRepository(
        connection
    )

    outcome_repository = SQLiteBessEngineeringValidationOutcomeRepository(
        connection
    )

    attempt = ProcessingAttempt(
        packet_id="PKT-0007",
        attempt_number=1,
        processed_at_utc=datetime(
            2026, 10, 2, 9, 30, 6,
            tzinfo=timezone.utc,
        ),
        status=ProcessingStatus.SUCCESS,
        diagnostics=(),
        source_timezone_used="Europe/Kyiv",
    )

    attempt_repository.save(attempt)

    limits = BessOperatingLimits(
        min_temperature_c=-20.0,
        max_temperature_c=55.0,
        min_soc_percent=10.0,
        max_soc_percent=95.0,
        max_charge_power_kw=100.0,
        max_discharge_power_kw=120.0,
    )

    resolved_limits = ResolvedBessLimits(
        limits=limits,
        source=BessLimitsSource.DEFAULT,
        reason=BessLimitsResolutionReason.EXTERNAL_NOT_FOUND,
    )

    soc_rule = BessSOCDischargingRule(
        full_power_soc_percent=20.0,
        reduced_power_soc_percent=10.0,
        reduced_power_fraction=0.5,
    )

    resolved_soc_rule = ResolvedBessSOCDischargingRule(
        rule=soc_rule,
        source=BessSOCDischargingRuleSource.DEFAULT,
        reason=BessSOCDischargingRuleResolutionReason.EXTERNAL_NOT_FOUND,
    )

    outcome = BessEngineeringValidationOutcome(
        validation_result=ValidationResult(),
        resolved_limits=resolved_limits,
        resolved_soc_rule=resolved_soc_rule,
    )

    outcome_repository.save(
        packet_id="PKT-0007",
        attempt_number=1,
        outcome=outcome,
    )

    restored_outcome = outcome_repository.get(
        packet_id="PKT-0007",
        attempt_number=1,
    )

    assert restored_outcome == outcome


