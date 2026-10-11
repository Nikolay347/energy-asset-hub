import sqlite3
from datetime import datetime, timezone

from energy_asset_hub.application.bess_packet_processing_service import (
    BessPacketProcessingService,
)
from energy_asset_hub.domain.models.ingress_telemetry_packet import (
    IngressTelemetryPacket,
)
from energy_asset_hub.infrastructure.persistence.sqlite.sqlite_processing_attempt_repository import (
    SQLiteProcessingAttemptRepository,
)
from energy_asset_hub.integrations.bess_api.processing_service import (
    BessTelemetryProcessingService,
)
from energy_asset_hub.infrastructure.persistence.sqlite.sqlite_measurement_repository import (
    SQLiteMeasurementRepository,
)

def test_service_persists_sequential_attempt_numbers_in_sqlite():
    connection = sqlite3.connect(":memory:")

    attempt_repository = SQLiteProcessingAttemptRepository(
        connection
    )
    measurement_repository = SQLiteMeasurementRepository(
        connection
    )

    service = BessPacketProcessingService(
        attempt_repository=attempt_repository,
        measurement_repository=measurement_repository,
        processing_service=BessTelemetryProcessingService(),
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

    first_result = service.process_packet(
        packet=packet,
        processed_at_utc=datetime(
            2026, 10, 2, 9, 30, 6,
            tzinfo=timezone.utc,
        ),
        source_timezone=None,
    )

    second_result = service.process_packet(
        packet=packet,
        processed_at_utc=datetime(
            2026, 10, 2, 9, 31, 0,
            tzinfo=timezone.utc,
        ),
        source_timezone=None,
    )

    restored_first = attempt_repository.get(
        packet_id="PKT-0007",
        attempt_number=1,
    )

    restored_second = attempt_repository.get(
        packet_id="PKT-0007",
        attempt_number=2,
    )

    assert first_result.attempt.attempt_number == 1
    assert second_result.attempt.attempt_number == 2

    assert restored_first == first_result.attempt
    assert restored_second == second_result.attempt


def test_service_persists_measurements_in_sqlite():
    connection = sqlite3.connect(":memory:")

    attempt_repository = SQLiteProcessingAttemptRepository(
        connection
    )

    measurement_repository = SQLiteMeasurementRepository(
        connection
    )

    service = BessPacketProcessingService(
        attempt_repository=attempt_repository,
        measurement_repository=measurement_repository,
        processing_service=BessTelemetryProcessingService(),
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

    result = service.process_packet(
        packet=packet,
        processed_at_utc=datetime(
            2026, 10, 2, 9, 30, 6,
            tzinfo=timezone.utc,
        ),
        source_timezone=None,
    )

    for measurement in result.measurements:
        restored_measurement = measurement_repository.get(
            packet_id=measurement.packet_id,
            attempt_number=measurement.attempt_number,
            asset_id=measurement.asset_id,
            parameter_name=measurement.parameter_name,
            timestamp_utc=measurement.timestamp_utc,
        )

        assert restored_measurement == measurement