import sqlite3
from datetime import datetime

from energy_asset_hub.domain.models.measurement import Measurement


class SQLiteMeasurementRepository:
    def __init__(self, connection: sqlite3.Connection):
        self._connection = connection
        self._create_table()

    def _create_table(self) -> None:
        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS measurements (
                packet_id TEXT NOT NULL,
                attempt_number INTEGER NOT NULL,
                asset_id TEXT NOT NULL,
                source_id TEXT NOT NULL,
                parameter_name TEXT NOT NULL,
                value REAL NOT NULL,
                unit TEXT NOT NULL,
                timestamp_utc TEXT NOT NULL,
                
                FOREIGN KEY (packet_id, attempt_number)
                    REFERENCES processing_attempts(packet_id, attempt_number)
            )
            """
        )

        self._connection.commit()

    def save(self, measurement: Measurement) -> None:
        self._connection.execute(
            """
            INSERT INTO measurements (
                packet_id,
                attempt_number,
                asset_id,
                source_id,
                parameter_name,
                value,
                unit,
                timestamp_utc
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                measurement.packet_id,
                measurement.attempt_number,
                measurement.asset_id,
                measurement.source_id,
                measurement.parameter_name,
                measurement.value,
                measurement.unit,
                measurement.timestamp_utc.isoformat(),
            ),
        )

        self._connection.commit()

    def get(
        self,
        packet_id,
        attempt_number,
        asset_id: str,
        parameter_name: str,
        timestamp_utc: datetime,
    ) -> Measurement | None:
        cursor = self._connection.execute(
            """
            SELECT
                packet_id,
                attempt_number,
                asset_id,
                source_id,
                parameter_name,
                value,
                unit,
                timestamp_utc
            FROM measurements
            WHERE packet_id = ?
              AND attempt_number = ?
              AND asset_id = ?
              AND parameter_name = ?
              AND timestamp_utc = ?
            """,
            (
                packet_id,
                attempt_number,
                asset_id,
                parameter_name,
                timestamp_utc.isoformat(),
            ),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return Measurement(
            packet_id=row[0],
            attempt_number=row[1],
            asset_id=row[2],
            source_id=row[3],
            parameter_name=row[4],
            value=row[5],
            unit=row[6],
            timestamp_utc=datetime.fromisoformat(row[7]),
        )