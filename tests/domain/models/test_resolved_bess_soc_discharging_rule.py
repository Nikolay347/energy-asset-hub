from energy_asset_hub.domain.models.bess_soc_discharging_rule import (
    BessSOCDischargingRule,
)
from energy_asset_hub.domain.models.resolved_bess_soc_discharging_rule import (
    BessSOCDischargingRuleResolutionReason,
    BessSOCDischargingRuleSource,
    ResolvedBessSOCDischargingRule,
)


def test_resolved_soc_discharging_rule_stores_rule_source_and_reason():
    rule = BessSOCDischargingRule(
        full_power_soc_percent=20.0,
        reduced_power_soc_percent=10.0,
        reduced_power_fraction=0.5,
    )

    resolved_rule = ResolvedBessSOCDischargingRule(
        rule=rule,
        source=BessSOCDischargingRuleSource.DEFAULT,
        reason=BessSOCDischargingRuleResolutionReason.EXTERNAL_NOT_FOUND,
    )

    assert resolved_rule.rule is rule
    assert resolved_rule.source is BessSOCDischargingRuleSource.DEFAULT
    assert (
        resolved_rule.reason
        is BessSOCDischargingRuleResolutionReason.EXTERNAL_NOT_FOUND
    )