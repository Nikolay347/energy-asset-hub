import json
import sqlite3
from datetime import datetime

from energy_asset_hub.domain.models.ingress_telemetry_packet import (
    IngressTelemetryPacket,
)


class SQLiteTelemetryPacketRepository:
    def __init__(self, connection: sqlite3.Connection):
        self._connection = connection
        self._create_table()

    def _create_table(self) -> None:
        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS telemetry_packets (
                packet_id TEXT PRIMARY KEY,
                source_id TEXT NOT NULL,
                received_at_utc TEXT NOT NULL,
                ingress_payload TEXT NOT NULL
            )
            """
        )

        self._connection.commit()

    def save(self, packet: IngressTelemetryPacket) -> None:
        existing_packet = self.get(packet.packet_id)

        if existing_packet is not None:
            if existing_packet != packet:
                raise ValueError(
                    f"Packet with id {packet.packet_id!r} already exists with different data"
                )

            return

        self._connection.execute(
            """
            INSERT INTO telemetry_packets (
                packet_id,
                source_id,
                received_at_utc,
                ingress_payload
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                packet.packet_id,
                packet.source_id,
                packet.received_at_utc.isoformat(),
                json.dumps(packet.to_dict()),
            ),
        )

        self._connection.commit()

    def get(self, packet_id: str) -> IngressTelemetryPacket | None:
        cursor = self._connection.execute(
            """
            SELECT
                packet_id,
                source_id,
                received_at_utc,
                ingress_payload
            FROM telemetry_packets
            WHERE packet_id = ?
            """,
            (packet_id,),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return self._row_to_packet(row)

    def find_by_source_id(
            self,
            source_id: str,
    ) -> tuple[IngressTelemetryPacket, ...]:
        cursor = self._connection.execute(
            """
            SELECT
                packet_id,
                source_id,
                received_at_utc,
                ingress_payload
            FROM telemetry_packets
            WHERE source_id = ?
            ORDER BY received_at_utc
            """,
            (source_id,),
        )

        rows = cursor.fetchall()

        return tuple(
            self._row_to_packet(row)
            for row in rows
        )

    def _row_to_packet(self, row) -> IngressTelemetryPacket:
        return IngressTelemetryPacket(
            packet_id=row[0],
            source_id=row[1],
            received_at_utc=datetime.fromisoformat(row[2]),
            ingress_payload=json.loads(row[3]),
        )

    def find_by_received_at_range(
            self,
            start_utc: datetime,
            end_utc: datetime,
    ) -> tuple[IngressTelemetryPacket, ...]:
        if start_utc > end_utc:
            raise ValueError("start_utc must be less than or equal to end_utc")

        cursor = self._connection.execute(
            """
            SELECT
                packet_id,
                source_id,
                received_at_utc,
                ingress_payload
            FROM telemetry_packets
            WHERE received_at_utc >= ?
              AND received_at_utc <= ?
            ORDER BY received_at_utc
            """,
            (
                start_utc.isoformat(),
                end_utc.isoformat(),
            ),
        )

        rows = cursor.fetchall()

        return tuple(
            self._row_to_packet(row)
            for row in rows
        )

    def find_by_source_id_and_received_at_range(
            self,
            source_id: str,
            start_utc: datetime,
            end_utc: datetime,
    ) -> tuple[IngressTelemetryPacket, ...]:
        if start_utc > end_utc:
            raise ValueError("start_utc must be less than or equal to end_utc")

        cursor = self._connection.execute(
            """
            SELECT
                packet_id,
                source_id,
                received_at_utc,
                ingress_payload
            FROM telemetry_packets
            WHERE source_id = ?
              AND received_at_utc >= ?
              AND received_at_utc <= ?
            ORDER BY received_at_utc
            """,
            (
                source_id,
                start_utc.isoformat(),
                end_utc.isoformat(),
            ),
        )

        rows = cursor.fetchall()

        return tuple(
            self._row_to_packet(row)
            for row in rows
        )
