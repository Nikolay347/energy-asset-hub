from energy_asset_hub.domain.models.bess_operating_limits import (
    BessOperatingLimits,
)
from energy_asset_hub.domain.models.resolved_bess_limits import (
    BessLimitsResolutionReason,
    BessLimitsSource,
    ResolvedBessLimits,
)


def test_resolved_bess_limits_stores_limits_and_source():
    limits = BessOperatingLimits(
        min_temperature_c=-20.0,
        max_temperature_c=55.0,
        min_soc_percent=10.0,
        max_soc_percent=95.0,
        max_charge_power_kw=100.0,
        max_discharge_power_kw=120.0,
    )

    resolved = ResolvedBessLimits(
        limits=limits,
        source=BessLimitsSource.DEFAULT,
        reason=BessLimitsResolutionReason.EXTERNAL_NOT_FOUND,
    )

    assert resolved.limits == limits
    assert resolved.source is BessLimitsSource.DEFAULT


def test_resolved_bess_limits_stores_resolution_reason():
    limits = BessOperatingLimits(
        min_temperature_c=-20.0,
        max_temperature_c=55.0,
        min_soc_percent=10.0,
        max_soc_percent=95.0,
        max_charge_power_kw=100.0,
        max_discharge_power_kw=120.0,
    )

    resolved = ResolvedBessLimits(
        limits=limits,
        source=BessLimitsSource.DEFAULT,
        reason=BessLimitsResolutionReason.EXTERNAL_NOT_FOUND,
    )

    assert resolved.reason is BessLimitsResolutionReason.EXTERNAL_NOT_FOUND