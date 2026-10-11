from typing import Protocol

from energy_asset_hub.domain.models.measurement import Measurement


class MeasurementRepository(Protocol):
    def save(self, measurement: Measurement) -> None:
        ...