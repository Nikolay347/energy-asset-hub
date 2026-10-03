from datetime import datetime, timezone
from energy_asset_hub.domain.models.processing_attempt import (
    ProcessingAttempt,
    ProcessingStatus,
)

from energy_asset_hub.domain.models.processing_attempt import (
    ProcessingAttempt,
)

from energy_asset_hub.domain.validation.enums import (
    IssueSeverity,
    ValidationIssueCode,
)
from energy_asset_hub.domain.validation.validation_issue import ValidationIssue



def test_processing_attempt_stores_packet_id_and_processing_time():
    processed_at_utc = datetime(
        2026, 10, 2, 13, 30, 0,
        tzinfo=timezone.utc,
    )

    attempt = ProcessingAttempt(
        packet_id="PKT-0007",
        processed_at_utc=processed_at_utc,
        status=ProcessingStatus.SUCCESS,
    )

    assert attempt.packet_id == "PKT-0007"
    assert attempt.processed_at_utc == processed_at_utc


def test_processing_attempt_stores_status():
    processed_at_utc = datetime(
        2026, 10, 2, 13, 30, 0,
        tzinfo=timezone.utc,
    )

    attempt = ProcessingAttempt(
        packet_id="PKT-0007",
        processed_at_utc=processed_at_utc,
        status=ProcessingStatus.FAILED,
    )

    assert attempt.status is ProcessingStatus.FAILED


def test_failed_processing_attempt_stores_diagnostics():
    issue = ValidationIssue(
        field_name="timestamp",
        code=ValidationIssueCode.TIMEZONE_REQUIRED,
        severity=IssueSeverity.ERROR,
        message="Source timezone is required",
        actual_value="2026-10-02T12:30:00",
        expected="timezone-aware timestamp or configured source timezone",
    )

    attempt = ProcessingAttempt(
        packet_id="PKT-0007",
        processed_at_utc=datetime(
            2026, 10, 2, 13, 30, 0,
            tzinfo=timezone.utc,
        ),
        status=ProcessingStatus.FAILED,
        diagnostics=(issue,),
    )

    assert attempt.diagnostics == (issue,)
    assert attempt.diagnostics[0].code is ValidationIssueCode.TIMEZONE_REQUIRED


def test_processing_attempt_stores_source_timezone_used():
    processed_at_utc = datetime(
        2026, 10, 2, 13, 30, 0,
        tzinfo=timezone.utc,
    )

    attempt = ProcessingAttempt(
        packet_id="PKT-0007",
        processed_at_utc=processed_at_utc,
        status=ProcessingStatus.SUCCESS,
        source_timezone_used="Europe/Kyiv",
    )

    assert attempt.source_timezone_used == "Europe/Kyiv"

