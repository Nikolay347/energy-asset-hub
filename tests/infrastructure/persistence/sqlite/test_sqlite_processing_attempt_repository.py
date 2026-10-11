import pytest
import sqlite3
from datetime import datetime, timezone

from energy_asset_hub.domain.models.processing_attempt import (
    ProcessingAttempt,
    ProcessingStatus,
)
from energy_asset_hub.infrastructure.persistence.sqlite.sqlite_processing_attempt_repository import (
    SQLiteProcessingAttemptRepository,
)
from energy_asset_hub.domain.models.ingress_telemetry_packet import (
    IngressTelemetryPacket,
)
from energy_asset_hub.infrastructure.persistence.sqlite.sqlite_telemetry_packet_repository import (
    SQLiteTelemetryPacketRepository,
)


def test_save_and_get_processing_attempt():
    connection = sqlite3.connect(":memory:")

    repository = SQLiteProcessingAttemptRepository(connection)

    attempt = ProcessingAttempt(
        packet_id="PKT-0007",
        attempt_number=1,
        processed_at_utc=datetime(
            2026,
            10,
            7,
            7,
            0,
            5,
            tzinfo=timezone.utc,
        ),
        status=ProcessingStatus.SUCCESS,
        source_timezone_used="Europe/Kyiv",
    )

    repository.save(attempt)

    restored_attempt = repository.get(
        packet_id="PKT-0007",
        attempt_number=1,
    )

    assert restored_attempt == attempt


from energy_asset_hub.domain.validation.validation_issue import (
    IssueSeverity,
    ValidationIssue,
    ValidationIssueCode,
)


def test_save_and_get_failed_attempt_preserves_diagnostics():
    connection = sqlite3.connect(":memory:")

    repository = SQLiteProcessingAttemptRepository(connection)

    issue = ValidationIssue(
        field_name="timestamp",
        code=ValidationIssueCode.TIMEZONE_REQUIRED,
        severity=IssueSeverity.ERROR,
        message="Source timezone is required",
        actual_value="2026-10-07T10:00:00",
        expected="timezone-aware timestamp or configured source timezone",
    )

    attempt = ProcessingAttempt(
        packet_id="PKT-0007",
        attempt_number=1,
        processed_at_utc=datetime(
            2026,
            10,
            7,
            7,
            0,
            5,
            tzinfo=timezone.utc,
        ),
        status=ProcessingStatus.FAILED,
        diagnostics=(issue,),
        source_timezone_used=None,
    )

    repository.save(attempt)

    restored_attempt = repository.get(
        packet_id="PKT-0007",
        attempt_number=1,
    )

    assert restored_attempt == attempt


def test_processing_attempt_cannot_reference_unknown_packet():
    connection = sqlite3.connect(":memory:")
    connection.execute("PRAGMA foreign_keys = ON")

    SQLiteTelemetryPacketRepository(connection)
    repository = SQLiteProcessingAttemptRepository(connection)

    attempt = ProcessingAttempt(
        packet_id="UNKNOWN-PACKET",
        attempt_number=1,
        processed_at_utc=datetime(
            2026, 10, 7, 7, 0, 5,
            tzinfo=timezone.utc,
        ),
        status=ProcessingStatus.SUCCESS,
        source_timezone_used="Europe/Kyiv",
    )

    with pytest.raises(sqlite3.IntegrityError):
        repository.save(attempt)


def test_processing_attempt_can_reference_existing_packet():
    connection = sqlite3.connect(":memory:")
    connection.execute("PRAGMA foreign_keys = ON")

    packet_repository = SQLiteTelemetryPacketRepository(connection)
    attempt_repository = SQLiteProcessingAttemptRepository(connection)

    packet = IngressTelemetryPacket(
        packet_id="PKT-0007",
        source_id="BESS-01-API",
        ingress_payload={
            "soc_percent": 72.5,
        },
        received_at_utc=datetime(
            2026, 10, 7, 7, 0, 0,
            tzinfo=timezone.utc,
        ),
    )

    packet_repository.save(packet)

    attempt = ProcessingAttempt(
        packet_id="PKT-0007",
        attempt_number=1,
        processed_at_utc=datetime(
            2026, 10, 7, 7, 0, 5,
            tzinfo=timezone.utc,
        ),
        status=ProcessingStatus.SUCCESS,
        source_timezone_used="Europe/Kyiv",
    )

    attempt_repository.save(attempt)

    restored_attempt = attempt_repository.get(
        packet_id="PKT-0007",
        attempt_number=1,
    )

    assert restored_attempt == attempt


def test_repository_allows_saving_same_attempt_again():
    connection = sqlite3.connect(":memory:")

    repository = SQLiteProcessingAttemptRepository(connection)

    attempt = ProcessingAttempt(
        packet_id="PKT-0007",
        attempt_number=1,
        processed_at_utc=datetime(
            2026, 10, 7, 7, 0, 5,
            tzinfo=timezone.utc,
        ),
        status=ProcessingStatus.SUCCESS,
        source_timezone_used="Europe/Kyiv",
    )

    repository.save(attempt)
    repository.save(attempt)

    restored_attempt = repository.get(
        packet_id="PKT-0007",
        attempt_number=1,
    )

    assert restored_attempt == attempt


def test_repository_rejects_same_packet_and_attempt_number_with_different_data():
    connection = sqlite3.connect(":memory:")

    repository = SQLiteProcessingAttemptRepository(connection)

    original_attempt = ProcessingAttempt(
        packet_id="PKT-0007",
        attempt_number=1,
        processed_at_utc=datetime(
            2026, 10, 7, 7, 0, 5,
            tzinfo=timezone.utc,
        ),
        status=ProcessingStatus.SUCCESS,
        source_timezone_used="Europe/Kyiv",
    )

    conflicting_attempt = ProcessingAttempt(
        packet_id="PKT-0007",
        attempt_number=1,
        processed_at_utc=datetime(
            2026, 10, 7, 7, 0, 5,
            tzinfo=timezone.utc,
        ),
        status=ProcessingStatus.FAILED,
        source_timezone_used="Europe/Kyiv",
    )

    repository.save(original_attempt)

    with pytest.raises(ValueError):
        repository.save(conflicting_attempt)


def test_repository_stores_multiple_attempts_for_same_packet():
    connection = sqlite3.connect(":memory:")
    connection.execute("PRAGMA foreign_keys = ON")

    packet_repository = SQLiteTelemetryPacketRepository(connection)
    attempt_repository = SQLiteProcessingAttemptRepository(connection)

    packet = IngressTelemetryPacket(
        packet_id="PKT-0007",
        source_id="BESS-01-API",
        ingress_payload={
            "asset_id": "BESS-01",
            "timestamp": "2026-10-02T12:30:00",
            "soc_percent": 72.5,
            "power_kw": -120.0,
            "temperature_c": 28.3,
        },
        received_at_utc=datetime(
            2026, 10, 2, 9, 30, 5,
            tzinfo=timezone.utc,
        ),
    )

    packet_repository.save(packet)

    first_attempt = ProcessingAttempt(
        packet_id="PKT-0007",
        attempt_number=1,
        processed_at_utc=datetime(
            2026, 10, 2, 9, 30, 6,
            tzinfo=timezone.utc,
        ),
        status=ProcessingStatus.FAILED,
        source_timezone_used=None,
    )

    second_attempt = ProcessingAttempt(
        packet_id="PKT-0007",
        attempt_number=2,
        processed_at_utc=datetime(
            2026, 10, 2, 10, 0, 0,
            tzinfo=timezone.utc,
        ),
        status=ProcessingStatus.SUCCESS,
        source_timezone_used="Europe/Kyiv",
    )

    attempt_repository.save(first_attempt)
    attempt_repository.save(second_attempt)

    restored_first = attempt_repository.get(
        packet_id="PKT-0007",
        attempt_number=1,
    )

    restored_second = attempt_repository.get(
        packet_id="PKT-0007",
        attempt_number=2,
    )

    assert restored_first == first_attempt
    assert restored_second == second_attempt


def test_get_latest_attempt_number_returns_none_when_packet_has_no_attempts():
    connection = sqlite3.connect(":memory:")

    repository = SQLiteProcessingAttemptRepository(connection)

    latest_attempt_number = repository.get_latest_attempt_number(
        packet_id="PKT-0007",
    )

    assert latest_attempt_number is None


def test_get_latest_attempt_number_returns_highest_number_for_packet():
    connection = sqlite3.connect(":memory:")

    repository = SQLiteProcessingAttemptRepository(connection)

    first_attempt = ProcessingAttempt(
        packet_id="PKT-0007",
        attempt_number=1,
        processed_at_utc=datetime(
            2026, 10, 9, 10, 0, 0,
            tzinfo=timezone.utc,
        ),
        status=ProcessingStatus.FAILED,
        source_timezone_used=None,
    )

    second_attempt = ProcessingAttempt(
        packet_id="PKT-0007",
        attempt_number=2,
        processed_at_utc=datetime(
            2026, 10, 9, 10, 5, 0,
            tzinfo=timezone.utc,
        ),
        status=ProcessingStatus.SUCCESS,
        source_timezone_used="Europe/Kyiv",
    )

    repository.save(first_attempt)
    repository.save(second_attempt)

    latest_attempt_number = repository.get_latest_attempt_number(
        packet_id="PKT-0007",
    )

    assert latest_attempt_number == 2


