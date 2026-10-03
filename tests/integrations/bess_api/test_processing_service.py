from datetime import datetime, timezone

from energy_asset_hub.domain.models.normalized_telemetry_packet import (
    NormalizedTelemetryPacket,
)
from energy_asset_hub.domain.models.processing_attempt import (
    ProcessingStatus,
)
from energy_asset_hub.domain.validation.enums import ValidationIssueCode
from energy_asset_hub.integrations.bess_api.processing_service import (
    BessTelemetryProcessingService,
)


def test_service_returns_failed_attempt_and_no_measurements_for_invalid_packet():
    packet = NormalizedTelemetryPacket(
        packet_id="PKT-0007",
        source_id="BESS-01-API",
        normalized_payload={
            "asset_id": "BESS-01",
            "timestamp": "2026-10-02T12:30:00",
            "soc_percent": 72.5,
            "power_kw": -120.0,
            "temperature_c": 28.3,
        },
        received_at_utc=datetime(
            2026, 10, 2, 9, 30, 5,
            tzinfo=timezone.utc,
        ),
    )

    service = BessTelemetryProcessingService()

    result = service.process_packet(
        packet=packet,
        processed_at_utc=datetime(
            2026, 10, 2, 9, 30, 6,
            tzinfo=timezone.utc,
        ),
        source_timezone=None,
    )

    assert result.attempt.status is ProcessingStatus.FAILED
    assert result.measurements == ()

    assert any(
        issue.code is ValidationIssueCode.TIMEZONE_REQUIRED
        for issue in result.attempt.diagnostics
    )


def test_service_returns_successful_attempt_and_measurements_for_valid_packet():
    packet = NormalizedTelemetryPacket(
        packet_id="PKT-0007",
        source_id="BESS-01-API",
        normalized_payload={
            "asset_id": "BESS-01",
            "timestamp": "2026-10-02T12:30:00",
            "soc_percent": 72.5,
            "power_kw": -120.0,
            "temperature_c": 28.3,
        },
        received_at_utc=datetime(
            2026, 10, 2, 9, 30, 5,
            tzinfo=timezone.utc,
        ),
    )

    service = BessTelemetryProcessingService()

    result = service.process_packet(
        packet=packet,
        processed_at_utc=datetime(
            2026, 10, 2, 9, 30, 6,
            tzinfo=timezone.utc,
        ),
        source_timezone="Europe/Kyiv",
    )

    assert result.attempt.status is ProcessingStatus.SUCCESS
    assert result.attempt.diagnostics == ()
    assert result.attempt.source_timezone_used == "Europe/Kyiv"

    assert len(result.measurements) == 3

    assert all(
        measurement.source_id == packet.source_id
        for measurement in result.measurements
    )

    assert all(
        measurement.timestamp_utc
        == datetime(2026, 10, 2, 9, 30, tzinfo=timezone.utc)
        for measurement in result.measurements
    )


def test_service_can_reprocess_same_packet_after_source_timezone_is_configured():
    packet = NormalizedTelemetryPacket(
        packet_id="PKT-0007",
        source_id="BESS-01-API",
        normalized_payload={
            "asset_id": "BESS-01",
            "timestamp": "2026-10-02T12:30:00",
            "soc_percent": 72.5,
            "power_kw": -120.0,
            "temperature_c": 28.3,
        },
        received_at_utc=datetime(
            2026, 10, 2, 9, 30, 5,
            tzinfo=timezone.utc,
        ),
    )

    service = BessTelemetryProcessingService()

    first_result = service.process_packet(
        packet=packet,
        processed_at_utc=datetime(
            2026, 10, 2, 9, 30, 6,
            tzinfo=timezone.utc,
        ),
        source_timezone=None,
    )

    assert first_result.attempt.status is ProcessingStatus.FAILED
    assert first_result.measurements == ()

    assert any(
        issue.code is ValidationIssueCode.TIMEZONE_REQUIRED
        for issue in first_result.attempt.diagnostics
    )

    second_result = service.process_packet(
        packet=packet,
        processed_at_utc=datetime(
            2026, 10, 2, 10, 0, 0,
            tzinfo=timezone.utc,
        ),
        source_timezone="Europe/Kyiv",
    )

    assert second_result.attempt.status is ProcessingStatus.SUCCESS
    assert second_result.attempt.diagnostics == ()
    assert second_result.attempt.source_timezone_used == "Europe/Kyiv"

    assert len(second_result.measurements) == 3

    assert all(
        measurement.timestamp_utc
        == datetime(2026, 10, 2, 9, 30, tzinfo=timezone.utc)
        for measurement in second_result.measurements
    )