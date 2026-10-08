from datetime import datetime
from typing import Protocol, runtime_checkable
from energy_asset_hub.domain.models.ingress_telemetry_packet import (
    IngressTelemetryPacket,
)


@runtime_checkable
class IngressTelemetryPacketRepository(Protocol):
    def save(self, packet: IngressTelemetryPacket) -> None:
        ...

    def get(
        self,
        packet_id: str,
    ) -> IngressTelemetryPacket | None:
        ...

    def find_by_source_id(
        self,
        source_id: str,
    ) -> tuple[IngressTelemetryPacket, ...]:
        ...

    def find_by_received_at_range(
        self,
        start_utc: datetime,
        end_utc: datetime,
    ) -> tuple[IngressTelemetryPacket, ...]:
        ...

    def find_by_source_id_and_received_at_range(
        self,
        source_id: str,
        start_utc: datetime,
        end_utc: datetime,
    ) -> tuple[IngressTelemetryPacket, ...]:
        ...


class InMemoryIngressTelemetryPacketRepository:
    def __init__(self):
        self._packets: dict[str, IngressTelemetryPacket] = {}

    def save(self, packet: IngressTelemetryPacket) -> None:
        existing_packet = self._packets.get(packet.packet_id)

        if existing_packet is not None and existing_packet != packet:
            raise ValueError(
                f"Packet with id {packet.packet_id!r} already exists with different data"
            )

        self._packets[packet.packet_id] = packet

    def get(self, packet_id: str) -> IngressTelemetryPacket | None:
        return self._packets.get(packet_id)

    def find_by_source_id(
            self,
            source_id: str,
    ) -> tuple[IngressTelemetryPacket, ...]:
        return tuple(
            sorted(
                (
                    packet
                    for packet in self._packets.values()
                    if packet.source_id == source_id
        ),
        key=lambda packet: packet.received_at_utc,
    )
)


    def find_by_received_at_range(
            self,
            start_utc: datetime,
            end_utc: datetime,
    ) -> tuple[IngressTelemetryPacket, ...]:
        if start_utc > end_utc:
            raise ValueError("start_utc must not be later than end_utc")

        return tuple(
            sorted(
                (
                    packet
                    for packet in self._packets.values()
                    if start_utc <= packet.received_at_utc <= end_utc
                ),
                key=lambda packet: packet.received_at_utc,
            )
        )

    def find_by_source_id_and_received_at_range(
            self,
            source_id: str,
            start_utc: datetime,
            end_utc: datetime,
    ) -> tuple[IngressTelemetryPacket, ...]:
        return tuple(
            packet
            for packet in self.find_by_received_at_range(
                start_utc=start_utc,
                end_utc=end_utc,
            )
            if packet.source_id == source_id
        )


