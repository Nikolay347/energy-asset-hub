from energy_asset_hub.domain.models.bess_soc_discharging_rule import (
    BessSOCDischargingRule,
)


def test_soc_discharging_rule_stores_configuration():
    rule = BessSOCDischargingRule(
        full_power_soc_percent=20.0,
        reduced_power_soc_percent=10.0,
        reduced_power_fraction=0.5,
    )

    assert rule.full_power_soc_percent == 20.0
    assert rule.reduced_power_soc_percent == 10.0
    assert rule.reduced_power_fraction == 0.5


import pytest


def test_soc_discharging_rule_rejects_reduced_soc_not_below_full_power_soc():
    with pytest.raises(ValueError):
        BessSOCDischargingRule(
            full_power_soc_percent=10.0,
            reduced_power_soc_percent=20.0,
            reduced_power_fraction=0.5,
        )



def test_soc_discharging_rule_rejects_fraction_above_one():
    with pytest.raises(ValueError):
        BessSOCDischargingRule(
            full_power_soc_percent=20.0,
            reduced_power_soc_percent=10.0,
            reduced_power_fraction=1.2,
        )


def test_soc_discharging_rule_rejects_negative_fraction():
    with pytest.raises(ValueError):
        BessSOCDischargingRule(
            full_power_soc_percent=20.0,
            reduced_power_soc_percent=10.0,
            reduced_power_fraction=-0.1,
        )


def test_soc_discharging_rule_rejects_reduced_soc_below_zero():
    with pytest.raises(ValueError):
        BessSOCDischargingRule(
            full_power_soc_percent=20.0,
            reduced_power_soc_percent=-1.0,
            reduced_power_fraction=0.5,
        )


def test_soc_discharging_rule_rejects_full_power_soc_above_100():
    with pytest.raises(ValueError):
        BessSOCDischargingRule(
            full_power_soc_percent=101.0,
            reduced_power_soc_percent=10.0,
            reduced_power_fraction=0.5,
        )

def test_soc_discharging_rule_allows_full_power_at_high_soc():
    rule = BessSOCDischargingRule(
        full_power_soc_percent=20.0,
        reduced_power_soc_percent=10.0,
        reduced_power_fraction=0.5,
    )

    fraction = rule.allowed_discharge_fraction(
        soc_percent=50.0,
    )

    assert fraction == 1.0


def test_soc_discharging_rule_allows_reduced_power_in_middle_soc_zone():
    rule = BessSOCDischargingRule(
        full_power_soc_percent=20.0,
        reduced_power_soc_percent=10.0,
        reduced_power_fraction=0.5,
    )

    fraction = rule.allowed_discharge_fraction(
        soc_percent=15.0,
    )

    assert fraction == 0.5


def test_soc_discharging_rule_blocks_discharge_below_reduced_soc():
    rule = BessSOCDischargingRule(
        full_power_soc_percent=20.0,
        reduced_power_soc_percent=10.0,
        reduced_power_fraction=0.5,
    )

    fraction = rule.allowed_discharge_fraction(
        soc_percent=5.0,
    )

    assert fraction == 0.0


def test_soc_discharging_rule_allows_full_power_at_full_power_boundary():
    rule = BessSOCDischargingRule(
        full_power_soc_percent=20.0,
        reduced_power_soc_percent=10.0,
        reduced_power_fraction=0.5,
    )

    fraction = rule.allowed_discharge_fraction(
        soc_percent=20.0,
    )

    assert fraction == 1.0


def test_soc_discharging_rule_allows_reduced_power_at_reduced_soc_boundary():
    rule = BessSOCDischargingRule(
        full_power_soc_percent=20.0,
        reduced_power_soc_percent=10.0,
        reduced_power_fraction=0.5,
    )

    fraction = rule.allowed_discharge_fraction(
        soc_percent=10.0,
    )

    assert fraction == 0.5