from datetime import datetime, timezone, timedelta
import pytest


from energy_asset_hub.domain.models.measurement import Measurement


def test_measurement_stores_parameter_and_source():
    timestamp = datetime(
        2026, 9, 30, 9, 0,
        tzinfo=timezone.utc,
    )

    measurement = Measurement(
        asset_id="BESS-01",
        source_id="BESS-01-API",
        parameter_name="soc_percent",
        value=72.5,
        unit="%",
        timestamp_utc=timestamp,
    )

    assert measurement.asset_id == "BESS-01"
    assert measurement.source_id == "BESS-01-API"
    assert measurement.parameter_name == "soc_percent"
    assert measurement.value == 72.5
    assert measurement.unit == "%"
    assert measurement.timestamp_utc == timestamp


def test_measurement_rejects_naive_timestamp():
    timestamp = datetime(2026, 9, 30, 12, 0)

    with pytest.raises(ValueError):
        Measurement(
            asset_id="BESS-01",
            source_id="BESS-01-API",
            parameter_name="soc_percent",
            value=72.5,
            unit="%",
            timestamp_utc=timestamp,
        )


def test_measurement_rejects_non_utc_timestamp():
    timestamp = datetime(
        2026, 9, 30, 12, 0,
        tzinfo=timezone(timedelta(hours=3)),
    )

    with pytest.raises(ValueError):
        Measurement(
            asset_id="BESS-01",
            source_id="BESS-01-API",
            parameter_name="soc_percent",
            value=72.5,
            unit="%",
            timestamp_utc=timestamp,
        )


def test_measurement_rejects_non_numeric_value():
    timestamp = datetime(
        2026, 9, 30, 9, 0,
        tzinfo=timezone.utc,
    )

    with pytest.raises(TypeError):
        Measurement(
            asset_id="BESS-01",
            source_id="BESS-01-API",
            parameter_name="soc_percent",
            value="seventy",
            unit="%",
            timestamp_utc=timestamp,
        )


def test_measurement_rejects_boolean_value():
    timestamp = datetime(
        2026, 9, 30, 9, 0,
        tzinfo=timezone.utc,
    )

    with pytest.raises(TypeError):
        Measurement(
            asset_id="BESS-01",
            source_id="BESS-01-API",
            parameter_name="soc_percent",
            value=True,
            unit="%",
            timestamp_utc=timestamp,
        )


def test_measurement_rejects_nan_value():
    timestamp = datetime(
        2026, 9, 30, 9, 0,
        tzinfo=timezone.utc,
    )

    with pytest.raises(ValueError):
        Measurement(
            asset_id="BESS-01",
            source_id="BESS-01-API",
            parameter_name="temperature_c",
            value=float("nan"),
            unit="°C",
            timestamp_utc=timestamp,
        )


@pytest.mark.parametrize(
    "invalid_value",
    [
        float("inf"),
        float("-inf"),
    ],
)
def test_measurement_rejects_infinite_value(invalid_value):
    timestamp = datetime(
        2026, 9, 30, 9, 0,
        tzinfo=timezone.utc,
    )

    with pytest.raises(ValueError):
        Measurement(
            asset_id="BESS-01",
            source_id="BESS-01-API",
            parameter_name="power_kw",
            value=invalid_value,
            unit="kW",
            timestamp_utc=timestamp,
        )