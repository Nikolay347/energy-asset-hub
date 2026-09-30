from energy_asset_hub.domain.time.timezone_database_check import (
    TimezoneDatabaseCheck,
)


def test_timezone_database_is_available():
    checker = TimezoneDatabaseCheck()

    result = checker.check()

    assert result is True