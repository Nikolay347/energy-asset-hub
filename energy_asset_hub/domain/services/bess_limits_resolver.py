from energy_asset_hub.domain.configuration.configured_bess_registry import (
    ConfiguredBessRegistry,
)
from energy_asset_hub.domain.configuration.default_bess_limits_registry import (
    DefaultBessLimitsRegistry,
)
from energy_asset_hub.domain.repositories.external_bess_limits_repository import (
    ExternalBessLimitsRepository,
    ExternalBessLimitsRepositoryUnavailableError,
)
from energy_asset_hub.domain.models.resolved_bess_limits import (
    BessLimitsSource,
    ResolvedBessLimits,
    BessLimitsResolutionReason,
)


class UnknownConfiguredBessError(Exception):
    pass


class BessLimitsResolver:
    def __init__(
        self,
        configured_registry: ConfiguredBessRegistry,
        default_registry: DefaultBessLimitsRegistry,
        external_repository: ExternalBessLimitsRepository,
    ):
        self._configured_registry = configured_registry
        self._default_registry = default_registry
        self._external_repository = external_repository

    def resolve(
        self,
        asset_id: str,
    ) -> ResolvedBessLimits:
        if not self._configured_registry.contains(asset_id):
            raise UnknownConfiguredBessError(
                f"BESS asset is not configured: {asset_id!r}"
            )

        try:
            external_limits = self._external_repository.get(asset_id)
        except ExternalBessLimitsRepositoryUnavailableError:
            return ResolvedBessLimits(
                limits=self._default_registry.get(asset_id),
                source=BessLimitsSource.DEFAULT,
                reason=BessLimitsResolutionReason.EXTERNAL_REPOSITORY_UNAVAILABLE,
            )

        if external_limits is not None:
            return ResolvedBessLimits(
                limits=external_limits,
                source=BessLimitsSource.EXTERNAL,
                reason=BessLimitsResolutionReason.EXTERNAL_FOUND,
            )

        return ResolvedBessLimits(
            limits=self._default_registry.get(asset_id),
            source=BessLimitsSource.DEFAULT,
            reason=BessLimitsResolutionReason.EXTERNAL_NOT_FOUND,
        )


