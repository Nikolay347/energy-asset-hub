from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AppSettings:
    asset_id: str
    source_id: str
    telemetry_url: str
    source_timezone: str | None
    sqlite_path: str


def build_default_app_settings() -> AppSettings:
    return AppSettings(
        asset_id="BESS-01",
        source_id="BESS-01-REST",
        telemetry_url="http://bess-device/telemetry",
        source_timezone="Europe/Kyiv",
        sqlite_path="energy_asset_hub.db",
    )


