import pytest

from energy_asset_hub.domain.repositories.external_bess_limits_repository import (
    ExternalBessLimitsRepositoryUnavailableError,
)
from energy_asset_hub.domain.repositories.external_bess_soc_discharging_rule_repository import (
    ExternalBessSOCDischargingRuleRepositoryUnavailableError,
)
from energy_asset_hub.infrastructure.external.unavailable_bess_limits_repository import (
    UnavailableBessLimitsRepository,
)
from energy_asset_hub.infrastructure.external.unavailable_bess_soc_discharging_rule_repository import (
    UnavailableBessSOCDischargingRuleRepository,
)


def test_unavailable_bess_limits_repository_reports_unavailability():
    repository = UnavailableBessLimitsRepository()

    with pytest.raises(
        ExternalBessLimitsRepositoryUnavailableError
    ):
        repository.get("BESS-01")


def test_unavailable_bess_soc_rule_repository_reports_unavailability():
    repository = UnavailableBessSOCDischargingRuleRepository()

    with pytest.raises(
        ExternalBessSOCDischargingRuleRepositoryUnavailableError
    ):
        repository.get("BESS-01")