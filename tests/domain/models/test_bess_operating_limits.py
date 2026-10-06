import pytest

from energy_asset_hub.domain.models.bess_operating_limits import (
    BessOperatingLimits,
)


def test_bess_operating_limits_stores_configured_values():
    limits = BessOperatingLimits(
        min_temperature_c=-20.0,
        max_temperature_c=55.0,
        min_soc_percent=10.0,
        max_soc_percent=95.0,
        max_charge_power_kw=100.0,
        max_discharge_power_kw=120.0,
    )

    assert limits.min_temperature_c == -20.0
    assert limits.max_temperature_c == 55.0
    assert limits.min_soc_percent == 10.0
    assert limits.max_soc_percent == 95.0
    assert limits.max_charge_power_kw == 100.0
    assert limits.max_discharge_power_kw == 120.0


def test_bess_operating_limits_rejects_temperature_min_above_max():
    with pytest.raises(ValueError):
        BessOperatingLimits(
            min_temperature_c=60.0,
            max_temperature_c=55.0,
            min_soc_percent=10.0,
            max_soc_percent=95.0,
            max_charge_power_kw=100.0,
            max_discharge_power_kw=120.0,
        )


def test_bess_operating_limits_rejects_soc_min_above_max():
    with pytest.raises(ValueError):
        BessOperatingLimits(
            min_temperature_c=-20.0,
            max_temperature_c=55.0,
            min_soc_percent=95.0,
            max_soc_percent=20.0,
            max_charge_power_kw=100.0,
            max_discharge_power_kw=120.0,
        )

def test_bess_operating_limits_rejects_soc_below_zero():
    with pytest.raises(ValueError):
        BessOperatingLimits(
            min_temperature_c=-20.0,
            max_temperature_c=55.0,
            min_soc_percent=-5.0,
            max_soc_percent=95.0,
            max_charge_power_kw=100.0,
            max_discharge_power_kw=120.0,
        )

def test_bess_operating_limits_rejects_soc_above_one_hundred():
    with pytest.raises(ValueError):
        BessOperatingLimits(
            min_temperature_c=-20.0,
            max_temperature_c=55.0,
            min_soc_percent=10.0,
            max_soc_percent=105.0,
            max_charge_power_kw=100.0,
            max_discharge_power_kw=120.0,
        )

def test_bess_operating_limits_rejects_negative_charge_power_limit():
    with pytest.raises(ValueError):
        BessOperatingLimits(
            min_temperature_c=-20.0,
            max_temperature_c=55.0,
            min_soc_percent=10.0,
            max_soc_percent=95.0,
            max_charge_power_kw=-100.0,
            max_discharge_power_kw=120.0,
        )


def test_bess_operating_limits_rejects_negative_discharge_power_limit():
    with pytest.raises(ValueError):
        BessOperatingLimits(
            min_temperature_c=-20.0,
            max_temperature_c=55.0,
            min_soc_percent=10.0,
            max_soc_percent=95.0,
            max_charge_power_kw=100.0,
            max_discharge_power_kw=-120.0,
        )


def test_bess_operating_limits_allows_zero_power_limits():
    limits = BessOperatingLimits(
        min_temperature_c=-20.0,
        max_temperature_c=55.0,
        min_soc_percent=10.0,
        max_soc_percent=95.0,
        max_charge_power_kw=0.0,
        max_discharge_power_kw=0.0,
    )

    assert limits.max_charge_power_kw == 0.0
    assert limits.max_discharge_power_kw == 0.0
