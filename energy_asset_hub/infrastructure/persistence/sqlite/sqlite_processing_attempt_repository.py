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
                attempt_id TEXT PRIMARY KEY,
                packet_id TEXT NOT NULL,
                processed_at_utc TEXT NOT NULL,
                status TEXT NOT NULL,
                source_timezone_used TEXT,
                FOREIGN KEY (packet_id)
                    REFERENCES telemetry_packets(packet_id)
            )
            """
        )

        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS processing_attempt_diagnostics (
                diagnostic_id INTEGER PRIMARY KEY AUTOINCREMENT,
                attempt_id TEXT NOT NULL,
                field_name TEXT NOT NULL,
                code TEXT NOT NULL,
                severity TEXT NOT NULL,
                message TEXT NOT NULL,
                actual_value TEXT,
                expected TEXT,
                FOREIGN KEY (attempt_id)
                    REFERENCES processing_attempts(attempt_id)
            )
            """
        )

        self._connection.commit()

    def save(self, attempt: ProcessingAttempt) -> None:
        existing_attempt = self.get(attempt.attempt_id)

        if existing_attempt is not None:
            if existing_attempt != attempt:
                raise ValueError(
                    f"Processing attempt with id {attempt.attempt_id!r} "
                    f"already exists with different data"
                )

            return

        self._connection.execute(
            """
            INSERT INTO processing_attempts (
                attempt_id,
                packet_id,
                processed_at_utc,
                status,
                source_timezone_used
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                attempt.attempt_id,
                attempt.packet_id,
                attempt.processed_at_utc.isoformat(),
                attempt.status.value,
                attempt.source_timezone_used,
            ),
        )

        for issue in attempt.diagnostics:
            self._connection.execute(
                """
                INSERT INTO processing_attempt_diagnostics (
                    attempt_id,
                    field_name,
                    code,
                    severity,
                    message,
                    actual_value,
                    expected
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    attempt.attempt_id,
                    issue.field_name,
                    issue.code.name,
                    issue.severity.value,
                    issue.message,
                    json.dumps(issue.actual_value),
                    json.dumps(issue.expected),
                ),
            )

        self._connection.commit()

    def get(self, attempt_id: str) -> ProcessingAttempt | None:
        cursor = self._connection.execute(
            """
            SELECT
                attempt_id,
                packet_id,
                processed_at_utc,
                status,
                source_timezone_used
            FROM processing_attempts
            WHERE attempt_id = ?
            """,
            (attempt_id,),
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
            WHERE attempt_id = ?
            ORDER BY diagnostic_id
            """,
            (attempt_id,),
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
            attempt_id=row[0],
            packet_id=row[1],
            processed_at_utc=datetime.fromisoformat(row[2]),
            status=ProcessingStatus(row[3]),
            diagnostics=diagnostics,
            source_timezone_used=row[4],
        )