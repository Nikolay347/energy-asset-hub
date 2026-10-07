from typing import Protocol, runtime_checkable

from energy_asset_hub.domain.models.bess_soc_discharging_rule import (
    BessSOCDischargingRule,
)


class ExternalBessSOCDischargingRuleRepositoryUnavailableError(Exception):
    pass


@runtime_checkable
class ExternalBessSOCDischargingRuleRepository(Protocol):
    def get(
        self,
        asset_id: str,
    ) -> BessSOCDischargingRule | None:
        ...