from datetime import datetime, timezone
from zoneinfo import ZoneInfo


class TimezoneRequiredError(ValueError):
    """Raised when timezone information is missing."""
    pass

class AmbiguousLocalTimeError(ValueError):
    """Raised when local time corresponds to two UTC instants."""
    pass

class NonexistentLocalTimeError(ValueError):
    """Raised when local time does not exist in the source timezone."""
    pass


class TimestampNormalizer:
    """Normalizes timestamps to UTC."""

    def normalize(
        self,
        raw_timestamp: str,
        source_timezone: str | None = None,
    ) -> datetime:

        parsed_timestamp = datetime.fromisoformat(raw_timestamp)

        if parsed_timestamp.tzinfo is None:
            if source_timezone is None:
                raise TimezoneRequiredError(
                    "Timestamp must contain timezone information "
                    "or source_timezone must be provided"
                )

            source_tz = ZoneInfo(source_timezone)

            first = parsed_timestamp.replace(
                tzinfo=source_tz,
                fold=0,
            )

            second = parsed_timestamp.replace(
                tzinfo=source_tz,
                fold=1,
            )

            first_utc = first.astimezone(timezone.utc)
            second_utc = second.astimezone(timezone.utc)

            first_roundtrip = first_utc.astimezone(source_tz)
            second_roundtrip = second_utc.astimezone(source_tz)

            first_is_valid = (
                    first_roundtrip.replace(tzinfo=None)
                    == parsed_timestamp
            )

            second_is_valid = (
                    second_roundtrip.replace(tzinfo=None)
                    == parsed_timestamp
            )

            if not first_is_valid and not second_is_valid:
                raise NonexistentLocalTimeError(
                    "Local timestamp does not exist in the source timezone"
                )

            if (
                    first_is_valid
                    and second_is_valid
                    and first_utc != second_utc
            ):
                raise AmbiguousLocalTimeError(
                    "Local timestamp is ambiguous in the source timezone"
                )

            parsed_timestamp = first

        return parsed_timestamp.astimezone(timezone.utc)