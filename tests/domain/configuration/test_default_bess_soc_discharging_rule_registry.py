import pytest
from energy_asset_hub.domain.configuration.default_bess_soc_discharging_rule_registry import (
    DefaultBessSOCDischargingRuleRegistry,
    BessDefaultSOCDischargingRuleNotFoundError,
)
from energy_asset_hub.domain.models.bess_soc_discharging_rule import (
    BessSOCDischargingRule,
)

def test_default_soc_discharging_rule_registry_returns_rule_for_asset():
    rule = BessSOCDischargingRule(
        full_power_soc_percent=20.0,
        reduced_power_soc_percent=10.0,
        reduced_power_fraction=0.5,
    )

    registry = DefaultBessSOCDischargingRuleRegistry(
        rules_by_asset={
            "BESS-01": rule,
        }
    )

    result = registry.get(
        asset_id="BESS-01",
    )

    assert result is rule


def test_default_soc_discharging_rule_registry_raises_error_for_unknown_asset():
    rule = BessSOCDischargingRule(
        full_power_soc_percent=20.0,
        reduced_power_soc_percent=10.0,
        reduced_power_fraction=0.5,
    )

    registry = DefaultBessSOCDischargingRuleRegistry(
        rules_by_asset={
            "BESS-01": rule,
        }
    )

    with pytest.raises(BessDefaultSOCDischargingRuleNotFoundError):
        registry.get(
            asset_id="BESS-UNKNOWN",
        )


def test_default_soc_discharging_rule_registry_is_not_affected_by_source_dict_changes():
    rule = BessSOCDischargingRule(
        full_power_soc_percent=20.0,
        reduced_power_soc_percent=10.0,
        reduced_power_fraction=0.5,
    )

    rules_by_asset = {
        "BESS-01": rule,
    }

    registry = DefaultBessSOCDischargingRuleRegistry(
        rules_by_asset=rules_by_asset,
    )

    rules_by_asset.clear()

    result = registry.get(
        asset_id="BESS-01",
    )

    assert result is rule


def test_default_soc_discharging_rule_registry_rejects_empty_configuration():
    with pytest.raises(ValueError):
        DefaultBessSOCDischargingRuleRegistry(
            rules_by_asset={},
        )
