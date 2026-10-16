from datetime import datetime, timezone

from energy_asset_hub.application.bess_packet_processing_service import (
    BessPacketProcessingService,
)
from energy_asset_hub.domain.models.ingress_telemetry_packet import (
    IngressTelemetryPacket,
)
from energy_asset_hub.domain.repositories.ingress_telemetry_packet_repository import IngressTelemetryPacketRepository
from energy_asset_hub.integrations.bess_api.processing_service import (
    BessTelemetryProcessingService,
)
from energy_asset_hub.domain.services.bess_engineering_validation_service import (
    BessEngineeringValidationService,
)
from energy_asset_hub.domain.models.bess_engineering_validation_outcome import (
    BessEngineeringValidationOutcome,
)
from energy_asset_hub.domain.models.bess_operating_limits import (
    BessOperatingLimits,
)
from energy_asset_hub.domain.models.bess_soc_discharging_rule import (
    BessSOCDischargingRule,
)
from energy_asset_hub.domain.models.resolved_bess_limits import (
    BessLimitsResolutionReason,
    BessLimitsSource,
    ResolvedBessLimits,
)
from energy_asset_hub.domain.models.resolved_bess_soc_discharging_rule import (
    BessSOCDischargingRuleResolutionReason,
    BessSOCDischargingRuleSource,
    ResolvedBessSOCDischargingRule,
)
from energy_asset_hub.domain.validation.validation_result import (
    ValidationResult,
)


class NoOpMeasurementRepository:
    def save(self, measurement) -> None:
        pass


class NoOpTelemetryPacketRepository(IngressTelemetryPacketRepository):
    def save(self, packet) -> None:
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


class NoOpBessEngineeringValidationService(
    BessEngineeringValidationService
):
    def __init__(self):
        pass

    def validate_asset_operating_conditions(
        self,
        asset_id: str,
        temperature_c: float,
        soc_percent: float,
        power_kw: float,
    ):
        pass


class NoOpEngineeringValidationOutcomeRepository:
    def save(
        self,
        packet_id: str,
        attempt_number: int,
        outcome,
    ) -> None:
        pass


class RecordingTelemetryPacketRepository:
    def __init__(self):
        self.saved_packets = []

    def save(self, packet):
        self.saved_packets.append(packet)


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
        engineering_validation_service=NoOpBessEngineeringValidationService(),
        engineering_validation_outcome_repository=(
            NoOpEngineeringValidationOutcomeRepository()
        ),
        packet_repository=NoOpTelemetryPacketRepository(),
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
        engineering_validation_service=NoOpBessEngineeringValidationService(),
        engineering_validation_outcome_repository=(
            NoOpEngineeringValidationOutcomeRepository()
        ),
        packet_repository=NoOpTelemetryPacketRepository(),
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
        engineering_validation_service=NoOpBessEngineeringValidationService(),
        engineering_validation_outcome_repository=(
            NoOpEngineeringValidationOutcomeRepository()
        ),
        packet_repository=NoOpTelemetryPacketRepository(),
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
        engineering_validation_service=NoOpBessEngineeringValidationService(),
        engineering_validation_outcome_repository=(
            NoOpEngineeringValidationOutcomeRepository()
        ),
        packet_repository=NoOpTelemetryPacketRepository(),
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


class RecordingEngineeringValidationService(
    BessEngineeringValidationService
):
    def __init__(self, outcome=None):
        self.calls = []
        self.outcome = outcome

    def validate_asset_operating_conditions(
        self,
        asset_id: str,
        temperature_c: float,
        soc_percent: float,
        power_kw: float,
    ):
        self.calls.append(
            {
                "asset_id": asset_id,
                "temperature_c": temperature_c,
                "soc_percent": soc_percent,
                "power_kw": power_kw,
            }
        )

        return self.outcome

def test_service_runs_engineering_validation_after_successful_processing():
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
    engineering_validation_service = (
        RecordingEngineeringValidationService()
    )

    service = BessPacketProcessingService(
        attempt_repository=attempt_repository,
        measurement_repository=measurement_repository,
        processing_service=BessTelemetryProcessingService(),
        engineering_validation_service=engineering_validation_service,
        engineering_validation_outcome_repository=(
            NoOpEngineeringValidationOutcomeRepository()
        ),
        packet_repository=NoOpTelemetryPacketRepository(),
    )

    service.process_packet(
        packet=packet,
        processed_at_utc=datetime(
            2026, 10, 2, 9, 30, 6,
            tzinfo=timezone.utc,
        ),
        source_timezone=None,
    )

    assert engineering_validation_service.calls == [
        {
            "asset_id": "BESS-01",
            "temperature_c": 28.3,
            "soc_percent": 72.5,
            "power_kw": -120.0,
        }
    ]


def test_service_does_not_run_engineering_validation_after_failed_processing():
    packet = IngressTelemetryPacket(
        packet_id="PKT-0007",
        source_id="BESS-01-API",
        ingress_payload={
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

    attempt_repository = RecordingProcessingAttemptRepository()
    measurement_repository = RecordingMeasurementRepository()
    engineering_validation_service = (
        RecordingEngineeringValidationService()
    )

    service = BessPacketProcessingService(
        attempt_repository=attempt_repository,
        measurement_repository=measurement_repository,
        processing_service=BessTelemetryProcessingService(),
        engineering_validation_service=engineering_validation_service,
        engineering_validation_outcome_repository=(
            NoOpEngineeringValidationOutcomeRepository()
        ),
        packet_repository=NoOpTelemetryPacketRepository(),
    )

    service.process_packet(
        packet=packet,
        processed_at_utc=datetime(
            2026, 10, 2, 9, 30, 6,
            tzinfo=timezone.utc,
        ),
        source_timezone=None,
    )

    assert engineering_validation_service.calls == []


class EventRecordingMeasurementRepository:
    def __init__(self, events):
        self.events = events

    def save(self, measurement) -> None:
        self.events.append("measurement_saved")


class EventRecordingEngineeringValidationService(
    BessEngineeringValidationService
):
    def __init__(self, events):
        self.events = events

    def validate_asset_operating_conditions(
        self,
        asset_id: str,
        temperature_c: float,
        soc_percent: float,
        power_kw: float,
    ):
        self.events.append("engineering_validation")


def test_service_runs_engineering_validation_before_saving_measurements():
    events = []

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

    service = BessPacketProcessingService(
        attempt_repository=RecordingProcessingAttemptRepository(),
        measurement_repository=EventRecordingMeasurementRepository(
            events
        ),
        processing_service=BessTelemetryProcessingService(),
        engineering_validation_service=(
            EventRecordingEngineeringValidationService(events)
        ),
        engineering_validation_outcome_repository=(
            NoOpEngineeringValidationOutcomeRepository()
        ),
        packet_repository=NoOpTelemetryPacketRepository(),
    )

    service.process_packet(
        packet=packet,
        processed_at_utc=datetime(
            2026, 10, 2, 9, 30, 6,
            tzinfo=timezone.utc,
        ),
        source_timezone=None,
    )

    assert events == [
        "engineering_validation",
        "measurement_saved",
        "measurement_saved",
        "measurement_saved",
    ]


class RecordingEngineeringValidationOutcomeRepository:
    def __init__(self):
        self.saved_items = []

    def save(
        self,
        packet_id: str,
        attempt_number: int,
        outcome,
    ) -> None:
        self.saved_items.append(
            {
                "packet_id": packet_id,
                "attempt_number": attempt_number,
                "outcome": outcome,
            }
        )

def create_engineering_validation_outcome():
    limits = BessOperatingLimits(
        min_temperature_c=-20.0,
        max_temperature_c=55.0,
        min_soc_percent=10.0,
        max_soc_percent=95.0,
        max_charge_power_kw=100.0,
        max_discharge_power_kw=120.0,
    )

    resolved_limits = ResolvedBessLimits(
        limits=limits,
        source=BessLimitsSource.DEFAULT,
        reason=BessLimitsResolutionReason.EXTERNAL_NOT_FOUND,
    )

    soc_rule = BessSOCDischargingRule(
        full_power_soc_percent=20.0,
        reduced_power_soc_percent=10.0,
        reduced_power_fraction=0.5,
    )

    resolved_soc_rule = ResolvedBessSOCDischargingRule(
        rule=soc_rule,
        source=BessSOCDischargingRuleSource.DEFAULT,
        reason=BessSOCDischargingRuleResolutionReason.EXTERNAL_NOT_FOUND,
    )

    return BessEngineeringValidationOutcome(
        validation_result=ValidationResult(issues=()),
        resolved_limits=resolved_limits,
        resolved_soc_rule=resolved_soc_rule,
    )


def test_service_saves_engineering_validation_outcome():
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

    outcome = create_engineering_validation_outcome()

    outcome_repository = (
        RecordingEngineeringValidationOutcomeRepository()
    )

    service = BessPacketProcessingService(
        attempt_repository=RecordingProcessingAttemptRepository(),
        measurement_repository=RecordingMeasurementRepository(),
        processing_service=BessTelemetryProcessingService(),
        engineering_validation_service=(
            RecordingEngineeringValidationService(
                outcome=outcome,
            )
        ),
        engineering_validation_outcome_repository=outcome_repository,
        packet_repository=NoOpTelemetryPacketRepository(),
    )

    result = service.process_packet(
        packet=packet,
        processed_at_utc=datetime(
            2026, 10, 2, 9, 30, 6,
            tzinfo=timezone.utc,
        ),
        source_timezone=None,
    )

    assert outcome_repository.saved_items == [
        {
            "packet_id": "PKT-0007",
            "attempt_number": result.attempt.attempt_number,
            "outcome": outcome,
        }
    ]


def test_service_saves_raw_packet():
    packet_repository = RecordingTelemetryPacketRepository()

    service = BessPacketProcessingService(
        attempt_repository=RecordingProcessingAttemptRepository(),
        measurement_repository=NoOpMeasurementRepository(),
        processing_service=BessTelemetryProcessingService(),
        engineering_validation_service=NoOpBessEngineeringValidationService(),
        engineering_validation_outcome_repository=(
            NoOpEngineeringValidationOutcomeRepository()
        ),
        packet_repository=packet_repository,
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

    service.process_packet(
        packet=packet,
        processed_at_utc=datetime(
            2026, 10, 2, 9, 30, 6,
            tzinfo=timezone.utc,
        ),
        source_timezone=None,
    )

    assert packet_repository.saved_packets == [packet]


class EventRecordingTelemetryPacketRepository:
    def __init__(self, events):
        self.events = events

    def save(self, packet) -> None:
        self.events.append("packet_saved")


class EventRecordingProcessingService:
    def __init__(self, events):
        self.events = events
        self._real_service = BessTelemetryProcessingService()

    def process_packet(
        self,
        packet,
        attempt_number,
        processed_at_utc,
        source_timezone,
    ):
        self.events.append("processing_started")

        return self._real_service.process_packet(
            packet=packet,
            attempt_number=attempt_number,
            processed_at_utc=processed_at_utc,
            source_timezone=source_timezone,
        )


def test_service_saves_raw_packet_before_processing():
    events = []

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

    service = BessPacketProcessingService(
        attempt_repository=RecordingProcessingAttemptRepository(),
        measurement_repository=NoOpMeasurementRepository(),
        processing_service=EventRecordingProcessingService(events),
        engineering_validation_service=NoOpBessEngineeringValidationService(),
        engineering_validation_outcome_repository=(
            NoOpEngineeringValidationOutcomeRepository()
        ),
        packet_repository=EventRecordingTelemetryPacketRepository(events),
    )

    service.process_packet(
        packet=packet,
        processed_at_utc=datetime(
            2026, 10, 2, 9, 30, 6,
            tzinfo=timezone.utc,
        ),
        source_timezone=None,
    )

    assert events == [
        "packet_saved",
        "processing_started",
    ]


