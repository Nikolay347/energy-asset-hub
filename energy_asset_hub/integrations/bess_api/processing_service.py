from dataclasses import dataclass
from datetime import datetime

from energy_asset_hub.domain.models.normalized_telemetry_packet import (
    NormalizedTelemetryPacket,
)
from energy_asset_hub.domain.models.processing_attempt import ProcessingAttempt
from energy_asset_hub.domain.models.measurement import Measurement
from energy_asset_hub.integrations.bess_api.processing_attempt_mapper import (
    BessProcessingAttemptMapper,
)
from energy_asset_hub.integrations.bess_api.telemetry_processor import (
    BessTelemetryProcessor,
)
from energy_asset_hub.integrations.bess_api.measurement_mapper import (
    BessMeasurementMapper,
)


@dataclass(frozen=True, slots=True)
class BessTelemetryProcessingServiceResult:
    attempt: ProcessingAttempt
    measurements: tuple[Measurement, ...]


class BessTelemetryProcessingService:
    def __init__(self):
        self._processor = BessTelemetryProcessor()
        self._attempt_mapper = BessProcessingAttemptMapper()
        self._measurement_mapper = BessMeasurementMapper()

    def process_packet(
        self,
        packet: NormalizedTelemetryPacket,
        processed_at_utc: datetime,
        source_timezone: str | None,
    ) -> BessTelemetryProcessingServiceResult:
        processing_result = self._processor.process(
            packet.to_dict(),
            source_timezone=source_timezone,
        )

        attempt = self._attempt_mapper.map(
            packet_id=packet.packet_id,
            processing_result=processing_result,
            processed_at_utc=processed_at_utc,
            source_timezone_used=source_timezone,
        )

        if processing_result.validation_result.is_valid:
            measurements = tuple(
                self._measurement_mapper.map(
                    processing_result=processing_result,
                    source_id=packet.source_id,
                )
            )

        else:
            measurements = ()

        return BessTelemetryProcessingServiceResult(
            attempt=attempt,
            measurements=measurements,
        )