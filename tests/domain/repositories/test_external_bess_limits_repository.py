from energy_asset_hub.domain.models.bess_operating_limits import (
    BessOperatingLimits,
)
from energy_asset_hub.domain.repositories.external_bess_limits_repository import (
    ExternalBessLimitsRepository,
)


class FakeExternalBessLimitsRepository:
    def __init__(
        self,
        limits_by_asset: dict[str, BessOperatingLimits],
    ):
        self._limits_by_asset = limits_by_asset

    def get(
        self,
        asset_id: str,
    ) -> BessOperatingLimits | None:
        return self._limits_by_asset.get(asset_id)


def test_repository_protocol_accepts_structurally_compatible_repository():
    repository = FakeExternalBessLimitsRepository(
        limits_by_asset={}
    )

    assert isinstance(
        repository,
        ExternalBessLimitsRepository,
    )