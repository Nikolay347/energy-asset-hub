from dataclasses import dataclass

from energy_asset_hub.domain.configuration.default_bess_limits_registry import (
    DefaultBessLimitsRegistry,
)
from energy_asset_hub.domain.configuration.default_bess_soc_discharging_rule_registry import (
    DefaultBessSOCDischargingRuleRegistry,
)
from energy_asset_hub.domain.models.bess_operating_limits import (
    BessOperatingLimits,
)
from energy_asset_hub.domain.models.bess_soc_discharging_rule import (
    BessSOCDischargingRule,
)


DEFAULT_BESS_LIMITS = BessOperatingLimits(
    min_temperature_c=-20.0,
    max_temperature_c=55.0,
    min_soc_percent=10.0,
    max_soc_percent=95.0,
    max_charge_power_kw=100.0,
    max_discharge_power_kw=120.0,
)

DEFAULT_BESS_SOC_RULE = BessSOCDischargingRule(
    full_power_soc_percent=20.0,
    reduced_power_soc_percent=10.0,
    reduced_power_fraction=0.5,
)


@dataclass(frozen=True, slots=True)
class BessDefaultRegistries:
    limits_registry: DefaultBessLimitsRegistry
    soc_rule_registry: DefaultBessSOCDischargingRuleRegistry


def build_default_bess_configuration() -> tuple[
    BessOperatingLimits,
    BessSOCDischargingRule,
]:
    return DEFAULT_BESS_LIMITS, DEFAULT_BESS_SOC_RULE


def build_bess_default_registries(
    asset_id: str,
    limits: BessOperatingLimits,
    soc_rule: BessSOCDischargingRule,
) -> BessDefaultRegistries:
    return BessDefaultRegistries(
        limits_registry=DefaultBessLimitsRegistry(
            limits_by_asset={
                asset_id: limits,
            }
        ),
        soc_rule_registry=DefaultBessSOCDischargingRuleRegistry(
            rules_by_asset={
                asset_id: soc_rule,
            }
        ),
    )


