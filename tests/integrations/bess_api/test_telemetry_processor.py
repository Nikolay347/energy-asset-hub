from datetime import datetime, timezone

from energy_asset_hub.integrations.bess_api.telemetry_processor import (
    BessTelemetryProcessor,
)
from energy_asset_hub.domain.validation.enums import (
    ValidationIssueCode,
)


def test_valid_payload_is_processed_with_source_timezone():
    processor = BessTelemetryProcessor()

    data = {
        "asset_id": "BESS-01",
        "timestamp": "2026-09-27T21:30:00",
        "soc_percent": 72.5,
        "power_kw": -120.0,
        "temperature_c": 28.3,
    }

    result = processor.process(
        data,
        source_timezone="Europe/Kyiv",
    )

    expected_timestamp = datetime(
        2026, 9, 27, 18, 30,
        tzinfo=timezone.utc,
    )

    assert result.validation_result.is_valid
    assert result.timestamp_utc == expected_timestamp


def test_invalid_payload_is_not_normalized():
    processor = BessTelemetryProcessor()

    data = {
        "asset_id": "BESS-01",
        "soc_percent": 72.5,
        "power_kw": -120.0,
        "temperature_c": 28.3,
    }

    result = processor.process(
        data,
        source_timezone="Europe/Kyiv",
    )

    assert not result.validation_result.is_valid
    assert result.timestamp_utc is None

    assert any(
        issue.code == ValidationIssueCode.MISSING_FIELD
        and issue.field_name == "timestamp"
        for issue in result.validation_result.issues
    )
    assert result.validated_payload is None


def test_missing_source_timezone_returns_validation_issue():
    processor = BessTelemetryProcessor()

    data = {
        "asset_id": "BESS-01",
        "timestamp": "2026-09-27T21:30:00",
        "soc_percent": 72.5,
        "power_kw": -120.0,
        "temperature_c": 28.3,
    }

    result = processor.process(data)

    assert not result.validation_result.is_valid
    assert result.timestamp_utc is None

    assert any(
        issue.code == ValidationIssueCode.TIMEZONE_REQUIRED
        and issue.field_name == "timestamp"
        for issue in result.validation_result.issues
    )

def test_ambiguous_local_timestamp_returns_validation_issue():
    processor = BessTelemetryProcessor()

    data = {
        "asset_id": "BESS-01",
        "timestamp": "2026-10-25T03:30:00",
        "soc_percent": 72.5,
        "power_kw": -120.0,
        "temperature_c": 28.3,
    }

    result = processor.process(
        data,
        source_timezone="Europe/Kyiv",
    )

    assert not result.validation_result.is_valid
    assert result.timestamp_utc is None

    assert any(
        issue.code == ValidationIssueCode.AMBIGUOUS_LOCAL_TIME
        and issue.field_name == "timestamp"
        for issue in result.validation_result.issues
    )


def test_nonexistent_local_timestamp_returns_validation_issue():
    processor = BessTelemetryProcessor()

    data = {
        "asset_id": "BESS-01",
        "timestamp": "2026-03-29T03:30:00",
        "soc_percent": 72.5,
        "power_kw": -120.0,
        "temperature_c": 28.3,
    }

    result = processor.process(
        data,
        source_timezone="Europe/Kyiv",
    )

    assert not result.validation_result.is_valid
    assert result.timestamp_utc is None

    assert any(
        issue.code == ValidationIssueCode.NONEXISTENT_LOCAL_TIME
        and issue.field_name == "timestamp"
        for issue in result.validation_result.issues
    )


def test_invalid_source_timezone_returns_validation_issue():
    processor = BessTelemetryProcessor()

    data = {
        "asset_id": "BESS-01",
        "timestamp": "2026-09-27T21:30:00",
        "soc_percent": 72.5,
        "power_kw": -120.0,
        "temperature_c": 28.3,
    }

    result = processor.process(
        data,
        source_timezone="Europe/Unknown",
    )

    assert not result.validation_result.is_valid
    assert result.timestamp_utc is None

    assert any(
        issue.code == ValidationIssueCode.INVALID_SOURCE_TIMEZONE
        and issue.field_name == "source_timezone"
        for issue in result.validation_result.issues
    )

def test_non_dict_payload_returns_validation_issue():
    processor = BessTelemetryProcessor()

    data = ["BESS-01", 72.5, 28.3]

    result = processor.process(data)

    assert not result.validation_result.is_valid
    assert result.timestamp_utc is None

    assert any(
        issue.code == ValidationIssueCode.INVALID_TYPE
        and issue.field_name is None
        for issue in result.validation_result.issues
    )


def test_timestamp_offset_takes_priority_over_source_timezone():
    processor = BessTelemetryProcessor()

    data = {
        "asset_id": "BESS-01",
        "timestamp": "2026-09-27T21:30:00+03:00",
        "soc_percent": 72.5,
        "power_kw": -120.0,
        "temperature_c": 28.3,
    }

    result = processor.process(
        data,
        source_timezone="Europe/Unknown",
    )

    expected_timestamp = datetime(
        2026, 9, 27, 18, 30,
        tzinfo=timezone.utc,
    )

    assert result.validation_result.is_valid
    assert result.validation_result.issues == ()
    assert result.timestamp_utc == expected_timestamp


def test_processing_result_preserves_validated_payload_snapshot():
    data = {
        "asset_id": "BESS-01",
        "timestamp": "2026-09-30T12:00:00+03:00",
        "soc_percent": 72.5,
        "power_kw": -120.0,
        "temperature_c": 28.3,
    }

    processor = BessTelemetryProcessor()

    result = processor.process(data)

    assert result.validation_result.is_valid

    assert result.validated_payload.asset_id == "BESS-01"
    assert result.validated_payload.soc_percent == 72.5

    data["soc_percent"] = 95.0

    assert result.validated_payload.soc_percent == 72.5