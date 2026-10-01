from datetime import datetime, timezone
import pytest

from energy_asset_hub.integrations.bess_api.telemetry_processor import (
    BessTelemetryProcessor,
)
from energy_asset_hub.integrations.bess_api.measurement_mapper import (
    BessMeasurementMapper,
)


def test_valid_bess_payload_creates_three_measurements():
    data = {
        "asset_id": "BESS-01",
        "timestamp": "2026-09-30T12:00:00+03:00",
        "soc_percent": 72.5,
        "power_kw": -120.0,
        "temperature_c": 28.3,
    }

    processor = BessTelemetryProcessor()
    processing_result = processor.process(data)

    assert processing_result.validation_result.is_valid

    mapper = BessMeasurementMapper()

    measurements = mapper.map(
        processing_result=processing_result,
        source_id="BESS-01-API",
    )

    assert len(measurements) == 3

    assert measurements[0].parameter_name == "soc_percent"
    assert measurements[0].value == 72.5
    assert measurements[0].unit == "%"

    assert measurements[1].parameter_name == "power_kw"
    assert measurements[1].value == -120.0
    assert measurements[1].unit == "kW"

    assert measurements[2].parameter_name == "temperature_c"
    assert measurements[2].value == 28.3
    assert measurements[2].unit == "°C"

    expected_timestamp = datetime(
        2026, 9, 30, 9, 0,
        tzinfo=timezone.utc,
    )

    for measurement in measurements:
        assert measurement.asset_id == "BESS-01"
        assert measurement.source_id == "BESS-01-API"
        assert measurement.timestamp_utc == expected_timestamp


def test_invalid_processing_result_is_rejected():
    data = {
        "asset_id": "BESS-01",
        "timestamp": "2026-09-30T12:00:00+03:00",
        "soc_percent": 150.0,
        "power_kw": -120.0,
        "temperature_c": 28.3,
    }

    processor = BessTelemetryProcessor()
    processing_result = processor.process(data)

    assert not processing_result.validation_result.is_valid
    assert processing_result.timestamp_utc is None

    mapper = BessMeasurementMapper()

    with pytest.raises(ValueError):
        mapper.map(
            processing_result=processing_result,
            source_id="BESS-01-API",
        )


def test_mapper_uses_validated_payload_snapshot():
    data = {
        "asset_id": "BESS-01",
        "timestamp": "2026-09-30T12:00:00+03:00",
        "soc_percent": 72.5,
        "power_kw": -120.0,
        "temperature_c": 28.3,
    }

    processor = BessTelemetryProcessor()

    processing_result = processor.process(data)

    assert processing_result.validation_result.is_valid

    # Змінюємо початковий словник після валідації.
    data["soc_percent"] = 95.0
    data["timestamp"] = "2026-09-30T12:01:00+03:00"

    mapper = BessMeasurementMapper()

    measurements = mapper.map(
        processing_result=processing_result,
        source_id="BESS-01-API",
    )

    assert measurements[0].value == 72.5

    assert measurements[0].timestamp_utc == datetime(
        2026, 9, 30, 9, 0,
        tzinfo=timezone.utc,
    )

