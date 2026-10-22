from energy_asset_hub.domain.repositories.external_bess_limits_repository import (
    ExternalBessLimitsRepositoryUnavailableError,
)


class UnavailableBessLimitsRepository:
    def get(self, asset_id: str):
        raise ExternalBessLimitsRepositoryUnavailableError(
            "External BESS limits repository is unavailable"
        )