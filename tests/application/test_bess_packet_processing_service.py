from datetime import datetime, timezone

from energy_asset_hub.application.bess_packet_processing_service import (
    BessPacketProcessingService,
)
from energy_asset_hub.domain.models.ingress_telemetry_packet import (
    IngressTelemetryPacket,
)
from energy_asset_hub.integrations.bess_api.processing_service import (
    BessTelemetryProcessingService,
)


class NoOpMeasurementRepository:
    def save(self, measurement) -> None:
        pass


class RecordingProcessingAttemptRepository:
    def __init__(
        self,
        latest_attempt_number: int | None = None,
    ):
        self._latest_attempt_number = latest_attempt_number
        self.saved_attempts = []

    def save(self, attempt) -> None:
        self.saved_attempts.append(attempt)

    def get(
        self,
        packet_id: str,
        attempt_number: int,
    ):
        return None

    def get_latest_attempt_number(
        self,
        packet_id: str,
    ) -> int | None:
        return self._latest_attempt_number


def test_service_assigns_first_attempt_number_when_packet_has_no_attempts():
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

    attempt_repository = RecordingProcessingAttemptRepository()

    service = BessPacketProcessingService(
        attempt_repository=attempt_repository,
        measurement_repository=NoOpMeasurementRepository(),
        processing_service=BessTelemetryProcessingService(),
    )

    result = service.process_packet(
        packet=packet,
        processed_at_utc=datetime(
            2026, 10, 2, 9, 30, 6,
            tzinfo=timezone.utc,
        ),
        source_timezone=None,
    )

    assert result.attempt.attempt_number == 1
    assert attempt_repository.saved_attempts == [
        result.attempt
    ]


def test_service_assigns_next_attempt_number_when_packet_has_previous_attempt():
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

    attempt_repository = RecordingProcessingAttemptRepository(
        latest_attempt_number=1,
    )

    service = BessPacketProcessingService(
        attempt_repository=attempt_repository,
        measurement_repository=NoOpMeasurementRepository(),
        processing_service=BessTelemetryProcessingService(),
    )

    result = service.process_packet(
        packet=packet,
        processed_at_utc=datetime(
            2026, 10, 2, 10, 0, 0,
            tzinfo=timezone.utc,
        ),
        source_timezone=None,
    )

    assert result.attempt.attempt_number == 2
    assert attempt_repository.saved_attempts == [
        result.attempt
    ]


class InMemoryProcessingAttemptRepository:
    def __init__(self):
        self._attempts = []

    def save(self, attempt) -> None:
        self._attempts.append(attempt)

    def get(
        self,
        packet_id: str,
        attempt_number: int,
    ):
        for attempt in self._attempts:
            if (
                attempt.packet_id == packet_id
                and attempt.attempt_number == attempt_number
            ):
                return attempt

        return None

    def get_latest_attempt_number(
        self,
        packet_id: str,
    ) -> int | None:
        attempt_numbers = [
            attempt.attempt_number
            for attempt in self._attempts
            if attempt.packet_id == packet_id
        ]

        if not attempt_numbers:
            return None

        return max(attempt_numbers)


def test_service_assigns_attempt_numbers_independently_for_different_packets():
    repository = InMemoryProcessingAttemptRepository()

    service = BessPacketProcessingService(
        attempt_repository=repository,
        measurement_repository=NoOpMeasurementRepository(),
        processing_service=BessTelemetryProcessingService(),
    )

    first_packet = IngressTelemetryPacket(
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

    second_packet = IngressTelemetryPacket(
        packet_id="PKT-0008",
        source_id="BESS-01-API",
        ingress_payload={
            "asset_id": "BESS-01",
            "timestamp": "2026-10-02T12:35:00+03:00",
            "soc_percent": 71.0,
            "power_kw": -110.0,
            "temperature_c": 28.5,
        },
        received_at_utc=datetime(
            2026, 10, 2, 9, 35, 5,
            tzinfo=timezone.utc,
        ),
    )

    first_result = service.process_packet(
        packet=first_packet,
        processed_at_utc=datetime(
            2026, 10, 2, 9, 30, 6,
            tzinfo=timezone.utc,
        ),
        source_timezone=None,
    )

    second_result = service.process_packet(
        packet=first_packet,
        processed_at_utc=datetime(
            2026, 10, 2, 9, 31, 0,
            tzinfo=timezone.utc,
        ),
        source_timezone=None,
    )

    third_result = service.process_packet(
        packet=second_packet,
        processed_at_utc=datetime(
            2026, 10, 2, 9, 35, 6,
            tzinfo=timezone.utc,
        ),
        source_timezone=None,
    )

    assert first_result.attempt.attempt_number == 1
    assert second_result.attempt.attempt_number == 2
    assert third_result.attempt.attempt_number == 1

class RecordingMeasurementRepository:
    def __init__(self):
        self.saved_measurements = []

    def save(self, measurement) -> None:
        self.saved_measurements.append(measurement)

def test_service_saves_measurements_from_successful_processing():
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

    attempt_repository = RecordingProcessingAttemptRepository()
    measurement_repository = RecordingMeasurementRepository()

    service = BessPacketProcessingService(
        attempt_repository=attempt_repository,
        measurement_repository=measurement_repository,
        processing_service=BessTelemetryProcessingService(),
    )

    result = service.process_packet(
        packet=packet,
        processed_at_utc=datetime(
            2026, 10, 2, 9, 30, 6,
            tzinfo=timezone.utc,
        ),
        source_timezone=None,
    )

    assert measurement_repository.saved_measurements == list(
        result.measurements
    )
