from typing import Protocol

from energy_asset_hub.domain.models.bess_engineering_validation_outcome import (
    BessEngineeringValidationOutcome,
)


class BessEngineeringValidationOutcomeRepository(Protocol):
    def save(
        self,
        packet_id: str,
        attempt_number: int,
        outcome: BessEngineeringValidationOutcome,
    ) -> None:
        ...


