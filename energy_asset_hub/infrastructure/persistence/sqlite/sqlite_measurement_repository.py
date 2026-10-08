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
                asset_id TEXT NOT NULL,
                source_id TEXT NOT NULL,
                parameter_name TEXT NOT NULL,
                value REAL NOT NULL,
                unit TEXT NOT NULL,
                timestamp_utc TEXT NOT NULL
            )
            """
        )

        self._connection.commit()

    def save(self, measurement: Measurement) -> None:
        self._connection.execute(
            """
            INSERT INTO measurements (
                asset_id,
                source_id,
                parameter_name,
                value,
                unit,
                timestamp_utc
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
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
        asset_id: str,
        parameter_name: str,
        timestamp_utc: datetime,
    ) -> Measurement | None:
        cursor = self._connection.execute(
            """
            SELECT
                asset_id,
                source_id,
                parameter_name,
                value,
                unit,
                timestamp_utc
            FROM measurements
            WHERE asset_id = ?
              AND parameter_name = ?
              AND timestamp_utc = ?
            """,
            (
                asset_id,
                parameter_name,
                timestamp_utc.isoformat(),
            ),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return Measurement(
            asset_id=row[0],
            source_id=row[1],
            parameter_name=row[2],
            value=row[3],
            unit=row[4],
            timestamp_utc=datetime.fromisoformat(row[5]),
        )