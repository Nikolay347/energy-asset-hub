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


class BessPacketProcessingService:
    def __init__(
        self,
        attempt_repository: ProcessingAttemptRepository,
        measurement_repository: MeasurementRepository,
        processing_service: BessTelemetryProcessingService,
    ):
        self._attempt_repository = attempt_repository
        self._measurement_repository = measurement_repository
        self._processing_service = processing_service

    def process_packet(
        self,
        packet: IngressTelemetryPacket,
        processed_at_utc: datetime,
        source_timezone: str | None,
    ):
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

        self._attempt_repository.save(result.attempt)

        for measurement in result.measurements:
            self._measurement_repository.save(measurement)

        return result