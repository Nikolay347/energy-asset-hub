from energy_asset_hub.config.bess_defaults import (
    build_bess_default_registries,
)
from energy_asset_hub.domain.models.bess_operating_limits import (
    BessOperatingLimits,
)
from energy_asset_hub.domain.models.bess_soc_discharging_rule import (
    BessSOCDischargingRule,
)


def test_build_bess_default_registries_maps_asset_to_defaults():
    limits = BessOperatingLimits(
        min_temperature_c=-20.0,
        max_temperature_c=55.0,
        min_soc_percent=10.0,
        max_soc_percent=95.0,
        max_charge_power_kw=100.0,
        max_discharge_power_kw=120.0,
    )

    soc_rule = BessSOCDischargingRule(
        full_power_soc_percent=20.0,
        reduced_power_soc_percent=10.0,
        reduced_power_fraction=0.5,
    )

    registries = build_bess_default_registries(
        asset_id="BESS-01",
        limits=limits,
        soc_rule=soc_rule,
    )

    assert registries.limits_registry.get("BESS-01") == limits
    assert registries.soc_rule_registry.get("BESS-01") == soc_rule