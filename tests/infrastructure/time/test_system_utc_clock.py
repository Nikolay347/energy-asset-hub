from datetime import timezone

from energy_asset_hub.infrastructure.time.system_utc_clock import (
    SystemUtcClock,
)


def test_system_utc_clock_returns_utc_datetime():
    clock = SystemUtcClock()

    current_time = clock.now_utc()

    assert current_time.tzinfo is timezone.utc




