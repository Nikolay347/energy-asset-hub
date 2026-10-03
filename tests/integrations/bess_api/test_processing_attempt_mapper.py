from datetime import datetime, timezone

from energy_asset_hub.domain.models.processing_attempt import (
    ProcessingStatus,
)
from energy_asset_hub.domain.validation.enums import (
    ValidationIssueCode,
)
from energy_asset_hub.integrations.bess_api.telemetry_processor import (
    BessTelemetryProcessor,
)
from energy_asset_hub.integrations.bess_api.processing_attempt_mapper import (
    BessProcessingAttemptMapper,
)


def test_failed_processing_result_is_mapped_to_failed_attempt():
    data = {
        "asset_id": "BESS-01",
        "timestamp": "2026-10-02T12:30:00",
        "soc_percent": 72.5,
        "power_kw": -120.0,
        "temperature_c": 28.3,
    }

    processor = BessTelemetryProcessor()

    processing_result = processor.process(data)

    processed_at_utc = datetime(
        2026, 10, 2, 9, 30, 6,
        tzinfo=timezone.utc,
    )

    mapper = BessProcessingAttemptMapper()

    attempt = mapper.map(
        packet_id="PKT-0007",
        processing_result=processing_result,
        processed_at_utc=processed_at_utc,
        source_timezone_used=None,
    )

    assert attempt.packet_id == "PKT-0007"
    assert attempt.processed_at_utc == processed_at_utc
    assert attempt.status is ProcessingStatus.FAILED
    assert attempt.source_timezone_used is None

    assert attempt.diagnostics == processing_result.validation_result.issues

    assert any(
        issue.code is ValidationIssueCode.TIMEZONE_REQUIRED
        for issue in attempt.diagnostics
    )


def test_successful_processing_result_is_mapped_to_successful_attempt():
    data = {
        "asset_id": "BESS-01",
        "timestamp": "2026-10-02T12:30:00",
        "soc_percent": 72.5,
        "power_kw": -120.0,
        "temperature_c": 28.3,
    }

    processor = BessTelemetryProcessor()

    processing_result = processor.process(
        data,
        source_timezone="Europe/Kyiv",
    )

    processed_at_utc = datetime(
        2026, 10, 2, 9, 30, 6,
        tzinfo=timezone.utc,
    )

    mapper = BessProcessingAttemptMapper()

    attempt = mapper.map(
        packet_id="PKT-0007",
        processing_result=processing_result,
        processed_at_utc=processed_at_utc,
        source_timezone_used="Europe/Kyiv",
    )

    assert attempt.status is ProcessingStatus.SUCCESS
    assert attempt.diagnostics == ()
    assert attempt.source_timezone_used == "Europe/Kyiv"