import sqlite3
from datetime import datetime, timezone

from energy_asset_hub.application.bess_packet_processing_service import (
    BessPacketProcessingService,
)
from energy_asset_hub.infrastructure.persistence.sqlite.sqlite_measurement_repository import (
    SQLiteMeasurementRepository,
)
from energy_asset_hub.infrastructure.persistence.sqlite.sqlite_processing_attempt_repository import (
    SQLiteProcessingAttemptRepository,
)
from energy_asset_hub.infrastructure.persistence.sqlite.sqlite_telemetry_packet_repository import (
    SQLiteTelemetryPacketRepository,
)
from energy_asset_hub.integrations.bess_api.bess_rest_telemetry_adapter import (
    BessRestTelemetryAdapter,
)
from energy_asset_hub.integrations.bess_api.processing_service import (
    BessTelemetryProcessingService,
)
from energy_asset_hub.domain.models.processing_attempt import (
    ProcessingStatus,
)


class FakeHttpResponse:
    def __init__(self, payload: dict):
        self._payload = payload

    def raise_for_status(self) -> None:
        pass

    def json(self) -> dict:
        return self._payload


class FakeHttpClient:
    def __init__(self, response: FakeHttpResponse):
        self._response = response

    def get(self, url: str):
        return self._response


class FakeClock:
    def __init__(self, now_utc: datetime):
        self._now_utc = now_utc

    def now_utc(self) -> datetime:
        return self._now_utc


class NoOpBessEngineeringValidationService:
    def validate_asset_operating_conditions(
        self,
        asset_id: str,
        temperature_c: float,
        soc_percent: float,
        power_kw: float,
    ):
        return None


class NoOpEngineeringValidationOutcomeRepository:
    def save(
        self,
        packet_id: str,
        attempt_number: int,
        outcome,
    ) -> None:
        pass


def test_rest_payload_is_processed_and_persisted_in_sqlite():
    connection = sqlite3.connect(":memory:")

    packet_repository = SQLiteTelemetryPacketRepository(connection)
    attempt_repository = SQLiteProcessingAttemptRepository(connection)
    measurement_repository = SQLiteMeasurementRepository(connection)

    payload = {
        "asset_id": "BESS-01",
        "timestamp": "2026-10-19T12:30:00+03:00",
        "soc_percent": 72.5,
        "power_kw": -120.0,
        "temperature_c": 28.3,
    }

    response = FakeHttpResponse(payload)
    http_client = FakeHttpClient(response)

    clock = FakeClock(
        datetime(
            2026, 10, 19, 9, 30, 5,
            tzinfo=timezone.utc,
        )
    )

    adapter = BessRestTelemetryAdapter(
        source_id="BESS-01-REST",
        http_client=http_client,
        telemetry_url="http://mock-bess/telemetry",
        clock=clock,
    )

    processing_service = BessPacketProcessingService(
        attempt_repository=attempt_repository,
        measurement_repository=measurement_repository,
        processing_service=BessTelemetryProcessingService(),
        engineering_validation_service=NoOpBessEngineeringValidationService(),
        engineering_validation_outcome_repository=(
            NoOpEngineeringValidationOutcomeRepository()
        ),
        packet_repository=packet_repository,
    )

    packet = adapter.fetch_packet()

    result = processing_service.process_packet(
        packet=packet,
        processed_at_utc=datetime(
            2026, 10, 19, 9, 30, 6,
            tzinfo=timezone.utc,
        ),
        source_timezone=None,
    )

    restored_packet = packet_repository.get(packet.packet_id)

    restored_attempt = attempt_repository.get(
        packet_id=packet.packet_id,
        attempt_number=1,
    )

    assert restored_packet == packet
    assert restored_attempt == result.attempt
    assert len(result.measurements) == 3


def test_invalid_timestamp_persists_raw_packet_and_failed_attempt():
    connection = sqlite3.connect(":memory:")

    packet_repository = SQLiteTelemetryPacketRepository(connection)
    attempt_repository = SQLiteProcessingAttemptRepository(connection)
    measurement_repository = SQLiteMeasurementRepository(connection)

    payload = {
        "asset_id": "BESS-01",
        "timestamp": "not-a-valid-timestamp",
        "soc_percent": 72.5,
        "power_kw": -120.0,
        "temperature_c": 28.3,
    }

    response = FakeHttpResponse(payload)
    http_client = FakeHttpClient(response)

    clock = FakeClock(
        datetime(
            2026, 10, 19, 9, 30, 5,
            tzinfo=timezone.utc,
        )
    )

    adapter = BessRestTelemetryAdapter(
        source_id="BESS-01-REST",
        http_client=http_client,
        telemetry_url="http://mock-bess/telemetry",
        clock=clock,
    )

    processing_service = BessPacketProcessingService(
        attempt_repository=attempt_repository,
        measurement_repository=measurement_repository,
        processing_service=BessTelemetryProcessingService(),
        engineering_validation_service=NoOpBessEngineeringValidationService(),
        engineering_validation_outcome_repository=(
            NoOpEngineeringValidationOutcomeRepository()
        ),
        packet_repository=packet_repository,
    )

    packet = adapter.fetch_packet()

    result = processing_service.process_packet(
        packet=packet,
        processed_at_utc=datetime(
            2026, 10, 19, 9, 30, 6,
            tzinfo=timezone.utc,
        ),
        source_timezone=None,
    )

    restored_packet = packet_repository.get(packet.packet_id)

    restored_attempt = attempt_repository.get(
        packet_id=packet.packet_id,
        attempt_number=1,
    )


    assert restored_packet == packet
    assert restored_attempt == result.attempt
    assert restored_attempt.status is ProcessingStatus.FAILED
    assert result.measurements == ()
