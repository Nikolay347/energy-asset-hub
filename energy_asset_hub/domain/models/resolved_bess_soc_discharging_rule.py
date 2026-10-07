from dataclasses import dataclass
from enum import Enum

from energy_asset_hub.domain.models.bess_soc_discharging_rule import (
    BessSOCDischargingRule,
)


class BessSOCDischargingRuleSource(Enum):
    DEFAULT = "default"
    EXTERNAL = "external"


class BessSOCDischargingRuleResolutionReason(Enum):
    EXTERNAL_FOUND = "external_found"
    EXTERNAL_NOT_FOUND = "external_not_found"
    EXTERNAL_REPOSITORY_UNAVAILABLE = "external_repository_unavailable"


@dataclass(frozen=True, slots=True)
class ResolvedBessSOCDischargingRule:
    rule: BessSOCDischargingRule
    source: BessSOCDischargingRuleSource
    reason: BessSOCDischargingRuleResolutionReason