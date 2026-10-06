from dataclasses import dataclass
from enum import Enum

from energy_asset_hub.domain.models.bess_operating_limits import (
    BessOperatingLimits,
)


class BessLimitsSource(Enum):
    DEFAULT = "default"
    EXTERNAL = "external"


class BessLimitsResolutionReason(Enum):
    EXTERNAL_FOUND = "external_found"
    EXTERNAL_NOT_FOUND = "external_not_found"
    EXTERNAL_REPOSITORY_UNAVAILABLE = "external_repository_unavailable"


@dataclass(frozen=True, slots=True)
class ResolvedBessLimits:
    limits: BessOperatingLimits
    source: BessLimitsSource
    reason: BessLimitsResolutionReason