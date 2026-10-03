from datetime import datetime, timezone

from energy_asset_hub.domain.models.normalized_telemetry_packet import (
    NormalizedTelemetryPacket,
)
from energy_asset_hub.domain.models.processing_attempt import (
    ProcessingStatus,
)
from energy_asset_hub.domain.validation.enums import ValidationIssueCode
from energy_asset_hub.integrations.bess_api.measurement_mapper import (
    BessMeasurementMapper,
)
from energy_asset_hub.integrations.bess_api.processing_attempt_mapper import (
    BessProcessingAttemptMapper,
)
from energy_asset_hub.integrations.bess_api.telemetry_processor import (
    BessTelemetryProcessor,
)


def test_packet_can_be_reprocessed_after_source_timezone_is_configured():
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

    processor = BessTelemetryProcessor()
    attempt_mapper = BessProcessingAttemptMapper()
    measurement_mapper = BessMeasurementMapper()

    first_result = processor.process(
        packet.to_dict()
    )

    first_attempt = attempt_mapper.map(
        packet_id=packet.packet_id,
        processing_result=first_result,
        processed_at_utc=datetime(
            2026, 10, 2, 9, 30, 6,
            tzinfo=timezone.utc,
        ),
        source_timezone_used=None,
    )

    assert first_attempt.status is ProcessingStatus.FAILED
    assert any(
        issue.code is ValidationIssueCode.TIMEZONE_REQUIRED
        for issue in first_attempt.diagnostics
    )
    assert first_result.validated_payload is None
    assert first_result.timestamp_utc is None

    second_result = processor.process(
        packet.to_dict(),
        source_timezone="Europe/Kyiv",
    )

    second_attempt = attempt_mapper.map(
        packet_id=packet.packet_id,
        processing_result=second_result,
        processed_at_utc=datetime(
            2026, 10, 2, 10, 0, 0,
            tzinfo=timezone.utc,
        ),
        source_timezone_used="Europe/Kyiv",
    )

    assert second_attempt.status is ProcessingStatus.SUCCESS
    assert second_attempt.diagnostics == ()
    assert second_attempt.source_timezone_used == "Europe/Kyiv"

    measurements = measurement_mapper.map(
        processing_result=second_result,
        source_id=packet.source_id,
    )

    assert len(measurements) == 3

    assert all(
        measurement.source_id == packet.source_id
        for measurement in measurements
    )

    assert all(
        measurement.timestamp_utc
        == datetime(2026, 10, 2, 9, 30, tzinfo=timezone.utc)
        for measurement in measurements
    )