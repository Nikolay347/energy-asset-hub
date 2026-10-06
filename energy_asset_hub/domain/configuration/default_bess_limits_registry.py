from energy_asset_hub.domain.models.bess_operating_limits import (
    BessOperatingLimits,
)


class BessDefaultLimitsNotFoundError(Exception):
    pass


class DefaultBessLimitsRegistry:
    def __init__(
        self,
        limits_by_asset: dict[str, BessOperatingLimits],
    ):
        if not limits_by_asset:
            raise ValueError(
                "Default BESS limits registry must not be empty"
            )

        self._limits_by_asset = dict(limits_by_asset)

    def get(
        self,
        asset_id: str,
    ) -> BessOperatingLimits:
        limits = self._limits_by_asset.get(asset_id)

        if limits is None:
            raise BessDefaultLimitsNotFoundError(
                f"Default BESS limits not found for asset_id={asset_id!r}"
            )

        return limits



