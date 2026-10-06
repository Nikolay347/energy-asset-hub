from typing import Protocol, runtime_checkable

from energy_asset_hub.domain.models.bess_operating_limits import (
    BessOperatingLimits,
)


class ExternalBessLimitsRepositoryUnavailableError(Exception):
    pass


@runtime_checkable
class ExternalBessLimitsRepository(Protocol):
    def get(
        self,
        asset_id: str,
    ) -> BessOperatingLimits | None:
        ...