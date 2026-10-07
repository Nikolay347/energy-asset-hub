from energy_asset_hub.domain.models.bess_soc_discharging_rule import (
    BessSOCDischargingRule,
)


class DefaultBessSOCDischargingRuleRegistry:
    def __init__(
        self,
        rules_by_asset: dict[str, BessSOCDischargingRule],
    ):
        if not rules_by_asset:
            raise ValueError(
                "rules_by_asset must not be empty"
            )

        self._rules_by_asset = dict(rules_by_asset)

    def get(
        self,
        asset_id: str,
    ) -> BessSOCDischargingRule:
        try:
            return self._rules_by_asset[asset_id]
        except KeyError as exc:
            raise BessDefaultSOCDischargingRuleNotFoundError(
                f"No default SOC discharging rule configured for asset '{asset_id}'"
            ) from exc


class BessDefaultSOCDischargingRuleNotFoundError(Exception):
    pass