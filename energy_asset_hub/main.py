from datetime import datetime
import sqlite3
from energy_asset_hub.config.app_settings import (
    AppSettings,
    build_default_app_settings,
)


from energy_asset_hub.bootstrap import build_bess_runtime
from energy_asset_hub.config.app_settings import AppSettings
from energy_asset_hub.config.bess_defaults import (
    build_bess_default_registries,
    build_default_bess_configuration,
)
from energy_asset_hub.domain.configuration.configured_bess_registry import (
    ConfiguredBessRegistry,
)
from energy_asset_hub.infrastructure.external.unavailable_bess_limits_repository import (
    UnavailableBessLimitsRepository,
)
from energy_asset_hub.infrastructure.external.unavailable_bess_soc_discharging_rule_repository import (
    UnavailableBessSOCDischargingRuleRepository,
)
from energy_asset_hub.infrastructure.time.system_utc_clock import (
    SystemUtcClock,
)


def run_from_default_settings() -> None:
    settings = build_default_app_settings()
    main(settings)


def run_bess_once(
    runtime,
    clock,
    source_timezone: str | None,
) -> None:
    packet = runtime.telemetry_adapter.fetch_packet()

    processed_at_utc = clock.now_utc()

    runtime.packet_processing_service.process_packet(
        packet=packet,
        processed_at_utc=processed_at_utc,
        source_timezone=source_timezone,
    )


def main(settings: AppSettings) -> None:
    connection = sqlite3.connect(settings.sqlite_path)

    try:
        limits, soc_rule = build_default_bess_configuration()

        default_registries = build_bess_default_registries(
            asset_id=settings.asset_id,
            limits=limits,
            soc_rule=soc_rule,
        )

        configured_registry = ConfiguredBessRegistry(
            asset_ids={settings.asset_id},
        )

        runtime = build_bess_runtime(
            source_id=settings.source_id,
            telemetry_url=settings.telemetry_url,
            connection=connection,
            configured_registry=configured_registry,
            default_limits_registry=default_registries.limits_registry,
            external_limits_repository=UnavailableBessLimitsRepository(),
            default_soc_rule_registry=default_registries.soc_rule_registry,
            external_soc_rule_repository=(
                UnavailableBessSOCDischargingRuleRepository()
            ),
        )

        run_bess_once(
            runtime=runtime,
            clock=SystemUtcClock(),
            source_timezone=settings.source_timezone,
        )
    finally:
        connection.close()


if __name__ == "__main__":
    run_from_default_settings()



