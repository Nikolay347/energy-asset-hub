import sqlite3
from datetime import datetime, timezone

from energy_asset_hub.domain.models.measurement import Measurement
from energy_asset_hub.infrastructure.persistence.sqlite.sqlite_measurement_repository import (
    SQLiteMeasurementRepository,
)


def test_save_and_get_measurement():
    connection = sqlite3.connect(":memory:")

    repository = SQLiteMeasurementRepository(connection)

    measurement = Measurement(
        asset_id="BESS-01",
        source_id="BESS-01-API",
        parameter_name="power_kw",
        value=70.0,
        unit="kW",
        timestamp_utc=datetime(
            2026,
            10,
            8,
            7,
            0,
            0,
            tzinfo=timezone.utc,
        ),
    )

    repository.save(measurement)

    restored_measurement = repository.get(
        asset_id="BESS-01",
        parameter_name="power_kw",
        timestamp_utc=datetime(
            2026,
            10,
            8,
            7,
            0,
            0,
            tzinfo=timezone.utc,
        ),
    )

    assert restored_measurement == measurement