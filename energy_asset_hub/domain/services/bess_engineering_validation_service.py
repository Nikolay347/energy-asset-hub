from energy_asset_hub.domain.models.bess_engineering_validation_outcome import (
    BessEngineeringValidationOutcome,
)
from energy_asset_hub.domain.models.bess_soc_discharging_rule import (
    BessSOCDischargingRule,
)


class BessEngineeringValidationService:
    def __init__(
        self,
        limits_resolver,
        soc_rule_resolver,
        validator,
    ):
        self._limits_resolver = limits_resolver
        self._soc_rule_resolver = soc_rule_resolver
        self._validator = validator

    def validate_asset_operating_conditions(
        self,
        asset_id: str,
        temperature_c: float,
        soc_percent: float,
        power_kw: float,
    ) -> BessEngineeringValidationOutcome:

        resolved_limits = self._limits_resolver.resolve(
            asset_id=asset_id,
        )

        resolved_soc_rule = self._soc_rule_resolver.resolve(
            asset_id=asset_id,
        )


        validation_result = self._validator.validate_operating_conditions(
            temperature_c=temperature_c,
            soc_percent=soc_percent,
            power_kw=power_kw,
            limits=resolved_limits.limits,
            soc_discharging_rule=resolved_soc_rule.rule,
        )


        return BessEngineeringValidationOutcome(
            validation_result=validation_result,
            resolved_limits=resolved_limits,
            resolved_soc_rule=resolved_soc_rule,
        )