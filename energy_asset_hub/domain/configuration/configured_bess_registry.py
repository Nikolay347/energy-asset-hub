class ConfiguredBessRegistry:
    def __init__(
        self,
        asset_ids: set[str],
    ):
        if not asset_ids:
            raise ValueError(
                "Configured BESS registry must not be empty"
            )

        self._asset_ids = set(asset_ids)

    def contains(
        self,
        asset_id: str,
    ) -> bool:
        return asset_id in self._asset_ids
