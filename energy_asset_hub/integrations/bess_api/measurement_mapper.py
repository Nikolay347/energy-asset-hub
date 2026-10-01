from energy_asset_hub.domain.models.measurement import Measurement
from energy_asset_hub.integrations.bess_api.telemetry_processor import (
    BessTelemetryProcessingResult,
)


class BessMeasurementMapper:
    _PARAMETER_MAPPING = (
        ("soc_percent", "%"),
        ("power_kw", "kW"),
        ("temperature_c", "°C"),
    )

    def map(
            self,
            processing_result: BessTelemetryProcessingResult,
            source_id: str,
    ) -> list[Measurement]:

        if (
                not processing_result.validation_result.is_valid
                or processing_result.timestamp_utc is None
                or processing_result.validated_payload is None
        ):
            raise ValueError(
                "Cannot create measurements from invalid telemetry"
            )

        payload = processing_result.validated_payload

        measurements = []

        for parameter_name, unit in self._PARAMETER_MAPPING:
            measurement = Measurement(
                asset_id=payload.asset_id,
                source_id=source_id,
                parameter_name=parameter_name,
                value=getattr(payload, parameter_name),
                unit=unit,
                timestamp_utc=processing_result.timestamp_utc,
            )

            measurements.append(measurement)

        return measurements