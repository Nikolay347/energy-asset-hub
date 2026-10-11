import json
import sqlite3
from datetime import datetime

from energy_asset_hub.domain.models.processing_attempt import (
    ProcessingAttempt,
    ProcessingStatus,
)
from energy_asset_hub.domain.validation.validation_issue import (
    IssueSeverity,
    ValidationIssue,
    ValidationIssueCode,
)


class SQLiteProcessingAttemptRepository:
    def __init__(self, connection: sqlite3.Connection):
        self._connection = connection
        self._create_tables()

    def _create_tables(self) -> None:
        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS processing_attempts (
                packet_id TEXT NOT NULL,
                attempt_number INTEGER NOT NULL,
                processed_at_utc TEXT NOT NULL,
                status TEXT NOT NULL,
                source_timezone_used TEXT,

PRIMARY KEY (packet_id, attempt_number),

FOREIGN KEY (packet_id)
    REFERENCES telemetry_packets(packet_id)
            )
            """
        )

        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS processing_attempt_diagnostics (
                diagnostic_id INTEGER PRIMARY KEY AUTOINCREMENT,
                packet_id TEXT NOT NULL,
                attempt_number INTEGER NOT NULL,
                field_name TEXT NOT NULL,
                code TEXT NOT NULL,
                severity TEXT NOT NULL,
                message TEXT NOT NULL,
                actual_value TEXT,
                expected TEXT,

    FOREIGN KEY (packet_id, attempt_number)
        REFERENCES processing_attempts(packet_id, attempt_number)
)
            """
        )

        self._connection.commit()

    def save(self, attempt: ProcessingAttempt) -> None:
        existing_attempt = self.get(
            packet_id=attempt.packet_id,
            attempt_number=attempt.attempt_number,
        )

        if existing_attempt is not None:
            if existing_attempt != attempt:
                raise ValueError(
                    f"Processing attempt for packet {attempt.packet_id!r} "
                    f"with attempt_number={attempt.attempt_number} "
                    f"already exists with different data"
                )

            return

        self._connection.execute(
            """
            INSERT INTO processing_attempts (
                packet_id,
                attempt_number,
                processed_at_utc,
                status,
                source_timezone_used
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                attempt.packet_id,
                attempt.attempt_number,
                attempt.processed_at_utc.isoformat(),
                attempt.status.value,
                attempt.source_timezone_used,
            ),
        )

        for issue in attempt.diagnostics:
            self._connection.execute(
                """
                INSERT INTO processing_attempt_diagnostics (
                    packet_id,
                    attempt_number,
                    field_name,
                    code,
                    severity,
                    message,
                    actual_value,
                    expected
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    attempt.packet_id,
                    attempt.attempt_number,
                    issue.field_name,
                    issue.code.name,
                    issue.severity.value,
                    issue.message,
                    json.dumps(issue.actual_value),
                    json.dumps(issue.expected),
                ),
            )

        self._connection.commit()

    def get(self, packet_id: str, attempt_number: int) -> ProcessingAttempt | None:
        cursor = self._connection.execute(
            """
            SELECT
                packet_id,
                attempt_number,
                processed_at_utc,
                status,
                source_timezone_used
            FROM processing_attempts
            WHERE packet_id = ?
                AND attempt_number = ?
            """,
            (packet_id, attempt_number),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        diagnostics_cursor = self._connection.execute(
            """
            SELECT
                field_name,
                code,
                severity,
                message,
                actual_value,
                expected
            FROM processing_attempt_diagnostics
            WHERE packet_id = ?
                AND attempt_number = ?
            ORDER BY diagnostic_id
            """,
            (packet_id, attempt_number),
        )

        diagnostic_rows = diagnostics_cursor.fetchall()

        diagnostics = tuple(
            ValidationIssue(
                field_name=diagnostic_row[0],
                code=ValidationIssueCode[diagnostic_row[1]],
                severity=IssueSeverity(diagnostic_row[2]),
                message=diagnostic_row[3],
                actual_value=json.loads(diagnostic_row[4]),
                expected=json.loads(diagnostic_row[5]),
            )
            for diagnostic_row in diagnostic_rows
        )

        return ProcessingAttempt(
            packet_id=row[0],
            attempt_number=row[1],
            processed_at_utc=datetime.fromisoformat(row[2]),
            status=ProcessingStatus(row[3]),
            diagnostics=diagnostics,
            source_timezone_used=row[4],
        )

    def get_latest_attempt_number(
            self,
            packet_id: str,
    ) -> int | None:
        cursor = self._connection.execute(
            """
            SELECT MAX(attempt_number)
            FROM processing_attempts
            WHERE packet_id = ?
            """,
            (packet_id,),
        )

        row = cursor.fetchone()

        return row[0]