from datetime import datetime, timezone
import pytest

from energy_asset_hub.domain.time.timestamp_normalizer import (
    TimestampNormalizer,
    TimezoneRequiredError,
    AmbiguousLocalTimeError,
    NonexistentLocalTimeError,
)


def test_timestamp_with_offset_is_normalized_to_utc():
    normalizer = TimestampNormalizer()

    raw_timestamp = "2026-09-27T21:30:00+03:00"

    result = normalizer.normalize(raw_timestamp)

    expected = datetime.fromisoformat(
        "2026-09-27T18:30:00+00:00"
    )

    assert result == expected
    assert result.tzinfo == timezone.utc


def test_timestamp_without_timezone_is_rejected():
    normalizer = TimestampNormalizer()

    raw_timestamp = "2026-09-27T21:30:00"

    with pytest.raises(TimezoneRequiredError):
        normalizer.normalize(raw_timestamp)

def test_timestamp_without_offset_uses_source_timezone():
    normalizer = TimestampNormalizer()

    raw_timestamp = "2026-09-27T21:30:00"

    result = normalizer.normalize(
        raw_timestamp,
        source_timezone="Europe/Kyiv",
    )

    expected = datetime.fromisoformat(
        "2026-09-27T18:30:00+00:00"
    )

    assert result == expected
    assert result.tzinfo == timezone.utc


def test_winter_timestamp_uses_correct_utc_offset():
    normalizer = TimestampNormalizer()

    raw_timestamp = "2026-12-15T21:30:00"

    result = normalizer.normalize(
        raw_timestamp,
        source_timezone="Europe/Kyiv",
    )

    expected = datetime.fromisoformat(
        "2026-12-15T19:30:00+00:00"
    )

    assert result == expected
    assert result.tzinfo == timezone.utc


def test_ambiguous_local_timestamp_is_rejected():
    normalizer = TimestampNormalizer()

    raw_timestamp = "2026-10-25T03:30:00"

    with pytest.raises(AmbiguousLocalTimeError):
        normalizer.normalize(
            raw_timestamp,
            source_timezone="Europe/Kyiv",
        )


def test_nonexistent_local_timestamp_is_rejected():
    normalizer = TimestampNormalizer()

    raw_timestamp = "2026-03-29T03:30:00"

    with pytest.raises(NonexistentLocalTimeError):
        normalizer.normalize(
            raw_timestamp,
            source_timezone="Europe/Kyiv",
        )

