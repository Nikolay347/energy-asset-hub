from energy_asset_hub.domain.models.bess_engineering_validation_outcome import (
    BessEngineeringValidationOutcome,
)
from energy_asset_hub.domain.models.bess_operating_limits import (
    BessOperatingLimits,
)
from energy_asset_hub.domain.models.resolved_bess_limits import (
    BessLimitsResolutionReason,
    BessLimitsSource,
    ResolvedBessLimits,
)
from energy_asset_hub.domain.validation.validation_result import ValidationResult
from energy_asset_hub.domain.models.bess_soc_discharging_rule import (
    BessSOCDischargingRule,
)
from energy_asset_hub.domain.models.resolved_bess_soc_discharging_rule import (
    BessSOCDischargingRuleResolutionReason,
    BessSOCDischargingRuleSource,
    ResolvedBessSOCDischargingRule,
)


def test_engineering_validation_outcome_stores_result_and_resolved_limits():
    limits = BessOperatingLimits(
        min_temperature_c=-20.0,
        max_temperature_c=55.0,
        min_soc_percent=10.0,
        max_soc_percent=95.0,
        max_charge_power_kw=100.0,
        max_discharge_power_kw=120.0,
    )

    resolved_limits = ResolvedBessLimits(
        limits=limits,
        source=BessLimitsSource.DEFAULT,
        reason=BessLimitsResolutionReason.EXTERNAL_NOT_FOUND,
    )

    soc_rule = BessSOCDischargingRule(
        full_power_soc_percent=20.0,
        reduced_power_soc_percent=10.0,
        reduced_power_fraction=0.5,
    )

    resolved_soc_rule = ResolvedBessSOCDischargingRule(
        rule=soc_rule,
        source=BessSOCDischargingRuleSource.DEFAULT,
        reason=BessSOCDischargingRuleResolutionReason.EXTERNAL_NOT_FOUND,
    )

    validation_result = ValidationResult(
        issues=(),
    )

    outcome = BessEngineeringValidationOutcome(
        validation_result=validation_result,
        resolved_limits=resolved_limits,
        resolved_soc_rule=resolved_soc_rule,
    )

    assert outcome.validation_result is validation_result
    assert outcome.resolved_limits is resolved_limits
    assert outcome.resolved_soc_rule is resolved_soc_rule


def test_engineering_validation_outcome_stores_resolved_soc_rule():
    limits = BessOperatingLimits(
        min_temperature_c=-20.0,
        max_temperature_c=55.0,
        min_soc_percent=10.0,
        max_soc_percent=95.0,
        max_charge_power_kw=100.0,
        max_discharge_power_kw=120.0,
    )

    resolved_limits = ResolvedBessLimits(
        limits=limits,
        source=BessLimitsSource.DEFAULT,
        reason=BessLimitsResolutionReason.EXTERNAL_NOT_FOUND,
    )

    soc_rule = BessSOCDischargingRule(
        full_power_soc_percent=20.0,
        reduced_power_soc_percent=10.0,
        reduced_power_fraction=0.5,
    )

    resolved_soc_rule = ResolvedBessSOCDischargingRule(
        rule=soc_rule,
        source=BessSOCDischargingRuleSource.DEFAULT,
        reason=BessSOCDischargingRuleResolutionReason.EXTERNAL_NOT_FOUND,
    )

    validation_result = ValidationResult(
        issues=(),
    )

    outcome = BessEngineeringValidationOutcome(
        validation_result=validation_result,
        resolved_limits=resolved_limits,
        resolved_soc_rule=resolved_soc_rule,
    )

    assert outcome.resolved_soc_rule is resolved_soc_rule