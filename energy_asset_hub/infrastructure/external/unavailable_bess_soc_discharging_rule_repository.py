from energy_asset_hub.domain.repositories.external_bess_soc_discharging_rule_repository import (
    ExternalBessSOCDischargingRuleRepositoryUnavailableError,
)


class UnavailableBessSOCDischargingRuleRepository:
    def get(self, asset_id: str):
        raise ExternalBessSOCDischargingRuleRepositoryUnavailableError(
            "External BESS SOC discharging rule repository is unavailable"
        )