from energy_asset_hub.domain.models.bess_soc_discharging_rule import (
    BessSOCDischargingRule,
)
from energy_asset_hub.domain.repositories.external_bess_soc_discharging_rule_repository import (
    ExternalBessSOCDischargingRuleRepository,
)


class FakeExternalBessSOCDischargingRuleRepository:
    def get(
        self,
        asset_id: str,
    ) -> BessSOCDischargingRule | None:
        return None


def test_fake_repository_matches_external_soc_discharging_rule_repository_protocol():
    repository = FakeExternalBessSOCDischargingRuleRepository()

    assert isinstance(
        repository,
        ExternalBessSOCDischargingRuleRepository,
    )