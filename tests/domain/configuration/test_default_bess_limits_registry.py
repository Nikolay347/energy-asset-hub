import pytest
from energy_asset_hub.domain.models.bess_operating_limits import (
    BessOperatingLimits,
)
from energy_asset_hub.domain.configuration.default_bess_limits_registry import (
    BessDefaultLimitsNotFoundError,
    DefaultBessLimitsRegistry,
)


def test_registry_returns_limits_for_asset_id():
    bess_01_limits = BessOperatingLimits(
        min_temperature_c=-20.0,
        max_temperature_c=55.0,
        min_soc_percent=10.0,
        max_soc_percent=95.0,
        max_charge_power_kw=100.0,
        max_discharge_power_kw=120.0,
    )

    registry = DefaultBessLimitsRegistry(
        limits_by_asset={
            "BESS-01": bess_01_limits,
        }
    )

    limits = registry.get("BESS-01")

    assert limits == bess_01_limits


def test_registry_returns_different_limits_for_different_assets():
    bess_01_limits = BessOperatingLimits(
        min_temperature_c=-20.0,
        max_temperature_c=55.0,
        min_soc_percent=10.0,
        max_soc_percent=95.0,
        max_charge_power_kw=100.0,
        max_discharge_power_kw=120.0,
    )

    bess_02_limits = BessOperatingLimits(
        min_temperature_c=-10.0,
        max_temperature_c=50.0,
        min_soc_percent=15.0,
        max_soc_percent=90.0,
        max_charge_power_kw=200.0,
        max_discharge_power_kw=250.0,
    )

    registry = DefaultBessLimitsRegistry(
        limits_by_asset={
            "BESS-01": bess_01_limits,
            "BESS-02": bess_02_limits,
        }
    )

    assert registry.get("BESS-01") == bess_01_limits
    assert registry.get("BESS-02") == bess_02_limits


def test_registry_is_not_changed_when_source_dict_is_modified():
    original_limits = BessOperatingLimits(
        min_temperature_c=-20.0,
        max_temperature_c=55.0,
        min_soc_percent=10.0,
        max_soc_percent=95.0,
        max_charge_power_kw=100.0,
        max_discharge_power_kw=120.0,
    )

    replacement_limits = BessOperatingLimits(
        min_temperature_c=-10.0,
        max_temperature_c=50.0,
        min_soc_percent=15.0,
        max_soc_percent=90.0,
        max_charge_power_kw=200.0,
        max_discharge_power_kw=250.0,
    )

    limits_by_asset = {
        "BESS-01": original_limits,
    }

    registry = DefaultBessLimitsRegistry(
        limits_by_asset=limits_by_asset,
    )

    limits_by_asset["BESS-01"] = replacement_limits

    assert registry.get("BESS-01") == original_limits


def test_registry_rejects_unknown_asset_id():
    known_limits = BessOperatingLimits(
        min_temperature_c=-20.0,
        max_temperature_c=55.0,
        min_soc_percent=10.0,
        max_soc_percent=95.0,
        max_charge_power_kw=100.0,
        max_discharge_power_kw=120.0,
    )

    registry = DefaultBessLimitsRegistry(
        limits_by_asset={
            "BESS-01": known_limits,
        }
    )

    with pytest.raises(BessDefaultLimitsNotFoundError):
        registry.get("BESS-UNKNOWN")


def test_registry_rejects_empty_limits_configuration():
    with pytest.raises(ValueError):
        DefaultBessLimitsRegistry(
            limits_by_asset={}
        )


