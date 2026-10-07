import pytest
from energy_asset_hub.domain.configuration.configured_bess_registry import (
    ConfiguredBessRegistry,
)
from energy_asset_hub.domain.configuration.default_bess_soc_discharging_rule_registry import (
    DefaultBessSOCDischargingRuleRegistry,
)
from energy_asset_hub.domain.models.bess_soc_discharging_rule import (
    BessSOCDischargingRule,
)
from energy_asset_hub.domain.models.resolved_bess_soc_discharging_rule import (
    BessSOCDischargingRuleResolutionReason,
    BessSOCDischargingRuleSource,
)
from energy_asset_hub.domain.services.bess_soc_discharging_rule_resolver import (
    BessSOCDischargingRuleResolver,
    UnknownConfiguredBessSOCDischargingRuleError,
)
from energy_asset_hub.domain.repositories.external_bess_soc_discharging_rule_repository import (
    ExternalBessSOCDischargingRuleRepositoryUnavailableError,
)


class FakeExternalBessSOCDischargingRuleRepository:
    def __init__(self, rule: BessSOCDischargingRule | None):
        self._rule = rule

    def get(
        self,
        asset_id: str,
    ) -> BessSOCDischargingRule | None:
        return self._rule


def test_resolver_returns_external_soc_discharging_rule_when_found():
    default_rule = BessSOCDischargingRule(
        full_power_soc_percent=20.0,
        reduced_power_soc_percent=10.0,
        reduced_power_fraction=0.5,
    )

    external_rule = BessSOCDischargingRule(
        full_power_soc_percent=25.0,
        reduced_power_soc_percent=15.0,
        reduced_power_fraction=0.4,
    )

    configured_registry = ConfiguredBessRegistry(
        asset_ids={"BESS-01"},
    )

    default_registry = DefaultBessSOCDischargingRuleRegistry(
        rules_by_asset={
            "BESS-01": default_rule,
        }
    )

    external_repository = FakeExternalBessSOCDischargingRuleRepository(
        rule=external_rule,
    )

    resolver = BessSOCDischargingRuleResolver(
        configured_registry=configured_registry,
        default_registry=default_registry,
        external_repository=external_repository,
    )

    result = resolver.resolve(
        asset_id="BESS-01",
    )

    assert result.rule is external_rule
    assert result.source is BessSOCDischargingRuleSource.EXTERNAL
    assert (
        result.reason
        is BessSOCDischargingRuleResolutionReason.EXTERNAL_FOUND
    )


def test_resolver_returns_default_soc_discharging_rule_when_external_not_found():
    default_rule = BessSOCDischargingRule(
        full_power_soc_percent=20.0,
        reduced_power_soc_percent=10.0,
        reduced_power_fraction=0.5,
    )

    configured_registry = ConfiguredBessRegistry(
        asset_ids={"BESS-01"},
    )

    default_registry = DefaultBessSOCDischargingRuleRegistry(
        rules_by_asset={
            "BESS-01": default_rule,
        }
    )

    external_repository = FakeExternalBessSOCDischargingRuleRepository(
        rule=None,
    )

    resolver = BessSOCDischargingRuleResolver(
        configured_registry=configured_registry,
        default_registry=default_registry,
        external_repository=external_repository,
    )

    result = resolver.resolve(
        asset_id="BESS-01",
    )

    assert result.rule is default_rule
    assert result.source is BessSOCDischargingRuleSource.DEFAULT
    assert (
        result.reason
        is BessSOCDischargingRuleResolutionReason.EXTERNAL_NOT_FOUND
    )


class UnavailableExternalBessSOCDischargingRuleRepository:
    def get(
        self,
        asset_id: str,
    ) -> BessSOCDischargingRule | None:
        raise ExternalBessSOCDischargingRuleRepositoryUnavailableError


def test_resolver_returns_default_rule_when_external_repository_is_unavailable():
    default_rule = BessSOCDischargingRule(
        full_power_soc_percent=20.0,
        reduced_power_soc_percent=10.0,
        reduced_power_fraction=0.5,
    )

    configured_registry = ConfiguredBessRegistry(
        asset_ids={"BESS-01"},
    )

    default_registry = DefaultBessSOCDischargingRuleRegistry(
        rules_by_asset={
            "BESS-01": default_rule,
        }
    )

    external_repository = (
        UnavailableExternalBessSOCDischargingRuleRepository()
    )

    resolver = BessSOCDischargingRuleResolver(
        configured_registry=configured_registry,
        default_registry=default_registry,
        external_repository=external_repository,
    )

    result = resolver.resolve(
        asset_id="BESS-01",
    )

    assert result.rule is default_rule
    assert result.source is BessSOCDischargingRuleSource.DEFAULT
    assert (
        result.reason
        is BessSOCDischargingRuleResolutionReason.EXTERNAL_REPOSITORY_UNAVAILABLE
    )


def test_resolver_raises_error_for_unknown_configured_bess():
    default_rule = BessSOCDischargingRule(
        full_power_soc_percent=20.0,
        reduced_power_soc_percent=10.0,
        reduced_power_fraction=0.5,
    )

    configured_registry = ConfiguredBessRegistry(
        asset_ids={"BESS-01"},
    )

    default_registry = DefaultBessSOCDischargingRuleRegistry(
        rules_by_asset={
            "BESS-01": default_rule,
        }
    )

    external_repository = FakeExternalBessSOCDischargingRuleRepository(
        rule=None,
    )

    resolver = BessSOCDischargingRuleResolver(
        configured_registry=configured_registry,
        default_registry=default_registry,
        external_repository=external_repository,
    )

    with pytest.raises(UnknownConfiguredBessSOCDischargingRuleError):
        resolver.resolve(
            asset_id="BESS-UNKNOWN",
        )