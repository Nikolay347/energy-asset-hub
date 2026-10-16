from datetime import datetime

from energy_asset_hub.domain.models.ingress_telemetry_packet import (
    IngressTelemetryPacket,
)
from energy_asset_hub.domain.repositories.processing_attempt_repository import (
    ProcessingAttemptRepository,
)
from energy_asset_hub.integrations.bess_api.processing_service import (
    BessTelemetryProcessingService,
)
from energy_asset_hub.domain.repositories.measurement_repository import (
    MeasurementRepository,
)
from energy_asset_hub.domain.services.bess_engineering_validation_service import (
    BessEngineeringValidationService,
)
from energy_asset_hub.domain.repositories.bess_engineering_validation_outcome_repository import (
    BessEngineeringValidationOutcomeRepository,
)
from energy_asset_hub.domain.repositories.ingress_telemetry_packet_repository import (
    IngressTelemetryPacketRepository,
)


class BessPacketProcessingService:
    def __init__(
        self,
        attempt_repository: ProcessingAttemptRepository,
        measurement_repository: MeasurementRepository,
        processing_service: BessTelemetryProcessingService,
        engineering_validation_service: BessEngineeringValidationService,
        engineering_validation_outcome_repository: BessEngineeringValidationOutcomeRepository,
        packet_repository: IngressTelemetryPacketRepository,
    ):
        self._attempt_repository = attempt_repository
        self._measurement_repository = measurement_repository
        self._processing_service = processing_service
        self._engineering_validation_service = engineering_validation_service
        self._engineering_validation_outcome_repository = (
            engineering_validation_outcome_repository
        )
        self._packet_repository = packet_repository

    def process_packet(
        self,
        packet: IngressTelemetryPacket,
        processed_at_utc: datetime,
        source_timezone: str | None,
    ):
        self._packet_repository.save(packet)
        latest_attempt_number = (
            self._attempt_repository.get_latest_attempt_number(
                packet.packet_id
            )
        )

        attempt_number = (
            1
            if latest_attempt_number is None
            else latest_attempt_number + 1
        )

        result = self._processing_service.process_packet(
            packet=packet,
            attempt_number=attempt_number,
            processed_at_utc=processed_at_utc,
            source_timezone=source_timezone,
        )

        engineering_validation_outcome = None

        if result.measurements:
            measurement_values = {
                measurement.parameter_name: measurement.value
                for measurement in result.measurements
            }

            engineering_validation_outcome = (
                self._engineering_validation_service.validate_asset_operating_conditions(
                    asset_id=result.measurements[0].asset_id,
                    temperature_c=measurement_values["temperature_c"],
                    soc_percent=measurement_values["soc_percent"],
                    power_kw=measurement_values["power_kw"],
                )
            )

        self._attempt_repository.save(result.attempt)

        for measurement in result.measurements:
            self._measurement_repository.save(measurement)

        if engineering_validation_outcome is not None:
            self._engineering_validation_outcome_repository.save(
                packet_id=packet.packet_id,
                attempt_number=result.attempt.attempt_number,
                outcome=engineering_validation_outcome,
            )

        return result

