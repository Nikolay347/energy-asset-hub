from dataclasses import dataclass

from energy_asset_hub.domain.models.resolved_bess_limits import ResolvedBessLimits
from energy_asset_hub.domain.validation.validation_result import ValidationResult
from energy_asset_hub.domain.models.resolved_bess_soc_discharging_rule import (
    ResolvedBessSOCDischargingRule,
)


@dataclass(frozen=True, slots=True)
class BessEngineeringValidationOutcome:
    validation_result: ValidationResult
    resolved_limits: ResolvedBessLimits
    resolved_soc_rule: ResolvedBessSOCDischargingRule