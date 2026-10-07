from energy_asset_hub.domain.models.bess_operating_limits import (
    BessOperatingLimits,
)
from energy_asset_hub.domain.models.resolved_bess_limits import (
    BessLimitsResolutionReason,
    BessLimitsSource,
    ResolvedBessLimits,
)
from energy_asset_hub.domain.services.bess_engineering_validation_service import (
    BessEngineeringValidationService,
)
from energy_asset_hub.domain.validation.bess_engineering_validator import (
    BessEngineeringValidator,
)
from energy_asset_hub.domain.models.bess_soc_discharging_rule import (
    BessSOCDischargingRule,
)
from energy_asset_hub.domain.models.resolved_bess_soc_discharging_rule import (
    BessSOCDischargingRuleResolutionReason,
    BessSOCDischargingRuleSource,
    ResolvedBessSOCDischargingRule,
)


class StubBessLimitsResolver:
    def __init__(self, resolved_limits: ResolvedBessLimits):
        self._resolved_limits = resolved_limits
        self.requested_asset_id = None

    def resolve(self, asset_id: str) -> ResolvedBessLimits:
        self.requested_asset_id = asset_id
        return self._resolved_limits


class StubBessSOCDischargingRuleResolver:
    def __init__(
        self,
        resolved_rule: ResolvedBessSOCDischargingRule,
    ):
        self._resolved_rule = resolved_rule
        self.requested_asset_id = None

    def resolve(
        self,
        asset_id: str,
    ) -> ResolvedBessSOCDischargingRule:
        self.requested_asset_id = asset_id
        return self._resolved_rule


def test_service_validates_operating_conditions_using_resolved_limits():
    limits = BessOperatingLimits(
        min_temperature_c=-20.0,
        max_temperature_c=55.0,
        min_soc_percent=10.0,
        max_soc_percent=95.0,
        max_charge_power_kw=100.0,
        max_discharge_power_kw=60.0,
    )

    resolved_limits = ResolvedBessLimits(
        limits=limits,
        source=BessLimitsSource.EXTERNAL,
        reason=BessLimitsResolutionReason.EXTERNAL_FOUND,
    )

    limits_resolver = StubBessLimitsResolver(
        resolved_limits=resolved_limits,
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

    soc_rule_resolver = StubBessSOCDischargingRuleResolver(
        resolved_rule=resolved_soc_rule,
    )

    service = BessEngineeringValidationService(
        limits_resolver=limits_resolver,
        soc_rule_resolver=soc_rule_resolver,
        validator=BessEngineeringValidator(),
    )

    outcome = service.validate_asset_operating_conditions(
        asset_id="BESS-01",
        temperature_c=25.0,
        soc_percent=50.0,
        power_kw=70.0,
    )

    assert limits_resolver.requested_asset_id == "BESS-01"
    assert outcome.resolved_limits is resolved_limits
    assert outcome.validation_result.is_valid is False
    assert len(outcome.validation_result.issues) == 1


def test_service_applies_soc_dependent_discharge_rule():
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
        source=BessLimitsSource.EXTERNAL,
        reason=BessLimitsResolutionReason.EXTERNAL_FOUND,
    )

    limits_resolver = StubBessLimitsResolver(
        resolved_limits=resolved_limits,
    )

    soc_discharging_rule = BessSOCDischargingRule(
        full_power_soc_percent=20.0,
        reduced_power_soc_percent=10.0,
        reduced_power_fraction=0.5,
    )

    resolved_soc_rule = ResolvedBessSOCDischargingRule(
        rule=soc_discharging_rule,
        source=BessSOCDischargingRuleSource.DEFAULT,
        reason=BessSOCDischargingRuleResolutionReason.EXTERNAL_NOT_FOUND,
    )

    soc_rule_resolver = StubBessSOCDischargingRuleResolver(
        resolved_rule=resolved_soc_rule,
    )

    service = BessEngineeringValidationService(
        limits_resolver=limits_resolver,
        soc_rule_resolver=soc_rule_resolver,
        validator=BessEngineeringValidator(),
    )

    outcome = service.validate_asset_operating_conditions(
        asset_id="BESS-01",
        temperature_c=25.0,
        soc_percent=15.0,
        power_kw=70.0,
    )

    assert outcome.validation_result.is_valid is False
    assert len(outcome.validation_result.issues) == 1


def test_service_resolves_and_applies_soc_discharging_rule():
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
        source=BessLimitsSource.EXTERNAL,
        reason=BessLimitsResolutionReason.EXTERNAL_FOUND,
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

    limits_resolver = StubBessLimitsResolver(
        resolved_limits=resolved_limits,
    )

    soc_rule_resolver = StubBessSOCDischargingRuleResolver(
        resolved_rule=resolved_soc_rule,
    )

    service = BessEngineeringValidationService(
        limits_resolver=limits_resolver,
        soc_rule_resolver=soc_rule_resolver,
        validator=BessEngineeringValidator(),
    )

    outcome = service.validate_asset_operating_conditions(
        asset_id="BESS-01",
        temperature_c=25.0,
        soc_percent=15.0,
        power_kw=70.0,
    )

    assert limits_resolver.requested_asset_id == "BESS-01"
    assert soc_rule_resolver.requested_asset_id == "BESS-01"

    assert outcome.validation_result.is_valid is False
    assert len(outcome.validation_result.issues) == 1

    issue = outcome.validation_result.issues[0]

    assert issue.field_name == "power_kw"
    assert issue.actual_value == 70.0
    assert issue.expected == "power_kw <= 60.0"

