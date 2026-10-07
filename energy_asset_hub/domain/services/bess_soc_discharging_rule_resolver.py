from energy_asset_hub.domain.models.resolved_bess_soc_discharging_rule import (
    BessSOCDischargingRuleResolutionReason,
    BessSOCDischargingRuleSource,
    ResolvedBessSOCDischargingRule,
)
from energy_asset_hub.domain.repositories.external_bess_soc_discharging_rule_repository import (
    ExternalBessSOCDischargingRuleRepositoryUnavailableError,
)


class BessSOCDischargingRuleResolver:
    def __init__(
        self,
        configured_registry,
        default_registry,
        external_repository,
    ):
        self._configured_registry = configured_registry
        self._default_registry = default_registry
        self._external_repository = external_repository

    def resolve(
        self,
        asset_id: str,
    ) -> ResolvedBessSOCDischargingRule:
        if not self._configured_registry.contains(asset_id):
            raise UnknownConfiguredBessSOCDischargingRuleError(
                f"BESS asset '{asset_id}' is not configured"
            )

        try:
            external_rule = self._external_repository.get(
                asset_id=asset_id,
            )
        except ExternalBessSOCDischargingRuleRepositoryUnavailableError:
            default_rule = self._default_registry.get(
                asset_id=asset_id,
            )

            return ResolvedBessSOCDischargingRule(
                rule=default_rule,
                source=BessSOCDischargingRuleSource.DEFAULT,
                reason=(
                    BessSOCDischargingRuleResolutionReason
                    .EXTERNAL_REPOSITORY_UNAVAILABLE
                ),
            )

        if external_rule is not None:
            return ResolvedBessSOCDischargingRule(
                rule=external_rule,
                source=BessSOCDischargingRuleSource.EXTERNAL,
                reason=BessSOCDischargingRuleResolutionReason.EXTERNAL_FOUND,
            )

        default_rule = self._default_registry.get(
            asset_id=asset_id,
        )

        return ResolvedBessSOCDischargingRule(
            rule=default_rule,
            source=BessSOCDischargingRuleSource.DEFAULT,
            reason=BessSOCDischargingRuleResolutionReason.EXTERNAL_NOT_FOUND,
        )


class UnknownConfiguredBessSOCDischargingRuleError(Exception):
    pass