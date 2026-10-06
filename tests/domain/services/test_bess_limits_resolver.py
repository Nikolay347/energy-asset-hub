import pytest
from energy_asset_hub.domain.configuration.configured_bess_registry import (
    ConfiguredBessRegistry,
)
from energy_asset_hub.domain.configuration.default_bess_limits_registry import (
    DefaultBessLimitsRegistry,
)
from energy_asset_hub.domain.models.bess_operating_limits import (
    BessOperatingLimits,
)
from energy_asset_hub.domain.services.bess_limits_resolver import (
    BessLimitsResolver,
    UnknownConfiguredBessError,
)
from energy_asset_hub.domain.repositories.external_bess_limits_repository import (
    ExternalBessLimitsRepositoryUnavailableError,
)
from energy_asset_hub.domain.models.resolved_bess_limits import (
    BessLimitsResolutionReason,
    BessLimitsSource,
)


class FakeExternalBessLimitsRepository:
    def __init__(
        self,
        limits_by_asset: dict[str, BessOperatingLimits],
    ):
        self._limits_by_asset = limits_by_asset

    def get(
        self,
        asset_id: str,
    ) -> BessOperatingLimits | None:
        return self._limits_by_asset.get(asset_id)


def test_resolver_returns_external_limits_when_available():
    default_limits = BessOperatingLimits(
        min_temperature_c=-20.0,
        max_temperature_c=55.0,
        min_soc_percent=10.0,
        max_soc_percent=95.0,
        max_charge_power_kw=100.0,
        max_discharge_power_kw=120.0,
    )

    external_limits = BessOperatingLimits(
        min_temperature_c=-15.0,
        max_temperature_c=50.0,
        min_soc_percent=15.0,
        max_soc_percent=90.0,
        max_charge_power_kw=80.0,
        max_discharge_power_kw=100.0,
    )

    configured_registry = ConfiguredBessRegistry(
        asset_ids={"BESS-01"},
    )

    default_registry = DefaultBessLimitsRegistry(
        limits_by_asset={
            "BESS-01": default_limits,
        }
    )

    external_repository = FakeExternalBessLimitsRepository(
        limits_by_asset={
            "BESS-01": external_limits,
        }
    )

    resolver = BessLimitsResolver(
        configured_registry=configured_registry,
        default_registry=default_registry,
        external_repository=external_repository,
    )

    resolved_limits = resolver.resolve("BESS-01")

    assert resolved_limits.limits == external_limits
    assert resolved_limits.source is BessLimitsSource.EXTERNAL
    assert resolved_limits.reason is BessLimitsResolutionReason.EXTERNAL_FOUND


def test_resolver_returns_default_limits_when_external_limits_are_missing():
    default_limits = BessOperatingLimits(
        min_temperature_c=-20.0,
        max_temperature_c=55.0,
        min_soc_percent=10.0,
        max_soc_percent=95.0,
        max_charge_power_kw=100.0,
        max_discharge_power_kw=120.0,
    )

    configured_registry = ConfiguredBessRegistry(
        asset_ids={"BESS-01"},
    )

    default_registry = DefaultBessLimitsRegistry(
        limits_by_asset={
            "BESS-01": default_limits,
        }
    )

    external_repository = FakeExternalBessLimitsRepository(
        limits_by_asset={}
    )

    resolver = BessLimitsResolver(
        configured_registry=configured_registry,
        default_registry=default_registry,
        external_repository=external_repository,
    )

    resolved_limits = resolver.resolve("BESS-01")

    assert resolved_limits.limits == default_limits
    assert resolved_limits.source is BessLimitsSource.DEFAULT
    assert resolved_limits.reason is BessLimitsResolutionReason.EXTERNAL_NOT_FOUND


def test_resolver_rejects_unknown_asset_id():
    default_limits = BessOperatingLimits(
        min_temperature_c=-20.0,
        max_temperature_c=55.0,
        min_soc_percent=10.0,
        max_soc_percent=95.0,
        max_charge_power_kw=100.0,
        max_discharge_power_kw=120.0,
    )

    configured_registry = ConfiguredBessRegistry(
        asset_ids={"BESS-01"},
    )

    default_registry = DefaultBessLimitsRegistry(
        limits_by_asset={
            "BESS-01": default_limits,
        }
    )

    external_repository = FakeExternalBessLimitsRepository(
        limits_by_asset={}
    )

    resolver = BessLimitsResolver(
        configured_registry=configured_registry,
        default_registry=default_registry,
        external_repository=external_repository,
    )

    with pytest.raises(UnknownConfiguredBessError):
        resolver.resolve("BESS-99")


class UnavailableExternalBessLimitsRepository:
    def get(
        self,
        asset_id: str,
    ) -> BessOperatingLimits | None:
        raise ExternalBessLimitsRepositoryUnavailableError(
            "External BESS limits repository is unavailable"
        )


def test_resolver_returns_default_limits_when_external_repository_is_unavailable():
    default_limits = BessOperatingLimits(
        min_temperature_c=-20.0,
        max_temperature_c=55.0,
        min_soc_percent=10.0,
        max_soc_percent=95.0,
        max_charge_power_kw=100.0,
        max_discharge_power_kw=120.0,
    )

    configured_registry = ConfiguredBessRegistry(
        asset_ids={"BESS-01"},
    )

    default_registry = DefaultBessLimitsRegistry(
        limits_by_asset={
            "BESS-01": default_limits,
        }
    )

    external_repository = UnavailableExternalBessLimitsRepository()

    resolver = BessLimitsResolver(
        configured_registry=configured_registry,
        default_registry=default_registry,
        external_repository=external_repository,
    )

    resolved_limits = resolver.resolve("BESS-01")

    assert resolved_limits.limits == default_limits
    assert resolved_limits.source is BessLimitsSource.DEFAULT
    assert (
            resolved_limits.reason
            is BessLimitsResolutionReason.EXTERNAL_REPOSITORY_UNAVAILABLE
    )