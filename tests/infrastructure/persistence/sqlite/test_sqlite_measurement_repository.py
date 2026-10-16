import sqlite3
import pytest
from datetime import datetime, timezone
from energy_asset_hub.domain.models.measurement import Measurement
from energy_asset_hub.infrastructure.persistence.sqlite.sqlite_measurement_repository import (
    SQLiteMeasurementRepository,
)
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


def test_save_and_get_measurement():
    connection = sqlite3.connect(":memory:")

    repository = SQLiteMeasurementRepository(connection)

    measurement = Measurement(
        packet_id="PKT-0007",
        attempt_number=1,
        asset_id="BESS-01",
        source_id="BESS-01-API",
        parameter_name="power_kw",
        value=70.0,
        unit="kW",
        timestamp_utc=datetime(2026, 10,8,7,0,0,
            tzinfo=timezone.utc,
        ),
    )

    repository.save(measurement)

    restored_measurement = repository.get(
        packet_id="PKT-0007",
        attempt_number=1,
        asset_id="BESS-01",
        parameter_name="power_kw",
        timestamp_utc=datetime(2026,10,8,7,0,0,
            tzinfo=timezone.utc,
        ),
    )

    assert restored_measurement == measurement


def test_save_and_get_measurement_preserves_traceability():
    connection = sqlite3.connect(":memory:")

    repository = SQLiteMeasurementRepository(connection)

    measurement = Measurement(
        packet_id="PKT-0007",
        attempt_number=2,
        asset_id="BESS-01",
        source_id="BESS-01-API",
        parameter_name="power_kw",
        value=70.0,
        unit="kW",
        timestamp_utc=datetime(2026,10,8,7,0,0,
            tzinfo=timezone.utc,
        ),
    )

    repository.save(measurement)

    restored_measurement = repository.get(
        packet_id="PKT-0007",
        attempt_number=2,
        asset_id="BESS-01",
        parameter_name="power_kw",
        timestamp_utc=datetime(2026,10,8,7,0,0,
            tzinfo=timezone.utc,
        ),
    )

    assert restored_measurement.packet_id == "PKT-0007"
    assert restored_measurement.attempt_number == 2


def test_save_measurement_rejects_missing_processing_attempt():
    connection = sqlite3.connect(":memory:")
    connection.execute("PRAGMA foreign_keys = ON")

    attempt_repository = SQLiteProcessingAttemptRepository(connection)
    measurement_repository = SQLiteMeasurementRepository(connection)

    measurement = Measurement(
        packet_id="PKT-0007",
        attempt_number=2,
        asset_id="BESS-01",
        source_id="BESS-01-API",
        parameter_name="power_kw",
        value=70.0,
        unit="kW",
        timestamp_utc=datetime(
            2026, 10, 8, 7, 0, 0,
            tzinfo=timezone.utc,
        ),
    )

    with pytest.raises(sqlite3.IntegrityError):
        measurement_repository.save(measurement)


def test_save_measurement_allows_if_existing_processing_attempt():
    connection = sqlite3.connect(":memory:")
    connection.execute("PRAGMA foreign_keys = ON")

    packet_repository = SQLiteTelemetryPacketRepository(connection)
    attempt_repository = SQLiteProcessingAttemptRepository(connection)
    measurement_repository = SQLiteMeasurementRepository(connection)

    packet = IngressTelemetryPacket(
        packet_id="PKT-0007",
        source_id="BESS-01-API",
        ingress_payload={
            "asset_id": "BESS-01",
            "timestamp": "2026-10-08T10:00:00+03:00",
            "soc_percent": 72.5,
            "power_kw": 70.0,
            "temperature_c": 28.3,
        },
        received_at_utc=datetime(
            2026, 10, 8, 7, 0, 0,
            tzinfo=timezone.utc,
        ),
    )

    packet_repository.save(packet)

    attempt = ProcessingAttempt(
        packet_id="PKT-0007",
        attempt_number=2,
        processed_at_utc=datetime(
            2026, 10, 8, 7, 0, 5,
            tzinfo=timezone.utc,
        ),
        status=ProcessingStatus.SUCCESS,
        source_timezone_used="Europe/Kyiv",
    )

    attempt_repository.save(attempt)

    measurement = Measurement(
        packet_id="PKT-0007",
        attempt_number=2,
        asset_id="BESS-01",
        source_id="BESS-01-API",
        parameter_name="power_kw",
        value=70.0,
        unit="kW",
        timestamp_utc=datetime(
            2026, 10, 8, 7, 0, 0,
            tzinfo=timezone.utc,
        ),
    )

    measurement_repository.save(measurement)

    restored_measurement = measurement_repository.get(
        packet_id="PKT-0007",
        attempt_number=2,
        asset_id="BESS-01",
        parameter_name="power_kw",
        timestamp_utc=datetime(
            2026, 10, 8, 7, 0, 0,
            tzinfo=timezone.utc,
        ),
    )

    assert restored_measurement == measurement
