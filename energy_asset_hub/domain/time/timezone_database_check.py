from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


class TimezoneDatabaseCheck:
    """Checks availability of required timezone data."""

    def check(self) -> bool:
        try:
            ZoneInfo("UTC")
            ZoneInfo("Europe/Kyiv")
            ZoneInfo("Europe/Warsaw")

        except ZoneInfoNotFoundError:
            return False

        return True