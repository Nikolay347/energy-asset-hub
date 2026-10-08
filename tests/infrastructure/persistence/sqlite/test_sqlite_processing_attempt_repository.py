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
from energy_asset_hub.domain.models.normalized_telemetry_packet import (
    NormalizedTelemetryPacket,
)
from energy_asset_hub.infrastructure.persistence.sqlite.sqlite_telemetry_packet_repository import (
    SQLiteTelemetryPacketRepository,
)


def test_save_and_get_processing_attempt():
    connection = sqlite3.connect(":memory:")

    repository = SQLiteProcessingAttemptRepository(connection)

    attempt = ProcessingAttempt(
        attempt_id="ATT-0001",
        packet_id="PKT-0007",
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

    restored_attempt = repository.get("ATT-0001")

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
        attempt_id="ATT-0001",
        packet_id="PKT-0007",
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

    restored_attempt = repository.get("ATT-0001")

    assert restored_attempt == attempt


def test_processing_attempt_cannot_reference_unknown_packet():
    connection = sqlite3.connect(":memory:")
    connection.execute("PRAGMA foreign_keys = ON")

    SQLiteTelemetryPacketRepository(connection)
    repository = SQLiteProcessingAttemptRepository(connection)

    attempt = ProcessingAttempt(
        attempt_id="ATT-0001",
        packet_id="UNKNOWN-PACKET",
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

    packet = NormalizedTelemetryPacket(
        packet_id="PKT-0007",
        source_id="BESS-01-API",
        normalized_payload={
            "soc_percent": 72.5,
        },
        received_at_utc=datetime(
            2026, 10, 7, 7, 0, 0,
            tzinfo=timezone.utc,
        ),
    )

    packet_repository.save(packet)

    attempt = ProcessingAttempt(
        attempt_id="ATT-0001",
        packet_id="PKT-0007",
        processed_at_utc=datetime(
            2026, 10, 7, 7, 0, 5,
            tzinfo=timezone.utc,
        ),
        status=ProcessingStatus.SUCCESS,
        source_timezone_used="Europe/Kyiv",
    )

    attempt_repository.save(attempt)

    restored_attempt = attempt_repository.get("ATT-0001")

    assert restored_attempt == attempt


def test_repository_allows_saving_same_attempt_again():
    connection = sqlite3.connect(":memory:")

    repository = SQLiteProcessingAttemptRepository(connection)

    attempt = ProcessingAttempt(
        attempt_id="ATT-0001",
        packet_id="PKT-0007",
        processed_at_utc=datetime(
            2026, 10, 7, 7, 0, 5,
            tzinfo=timezone.utc,
        ),
        status=ProcessingStatus.SUCCESS,
        source_timezone_used="Europe/Kyiv",
    )

    repository.save(attempt)
    repository.save(attempt)

    restored_attempt = repository.get("ATT-0001")

    assert restored_attempt == attempt


def test_repository_rejects_same_attempt_id_with_different_data():
    connection = sqlite3.connect(":memory:")

    repository = SQLiteProcessingAttemptRepository(connection)

    original_attempt = ProcessingAttempt(
        attempt_id="ATT-0001",
        packet_id="PKT-0007",
        processed_at_utc=datetime(
            2026, 10, 7, 7, 0, 5,
            tzinfo=timezone.utc,
        ),
        status=ProcessingStatus.SUCCESS,
        source_timezone_used="Europe/Kyiv",
    )

    conflicting_attempt = ProcessingAttempt(
        attempt_id="ATT-0001",
        packet_id="PKT-0007",
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