from datetime import datetime
from typing import Protocol

from energy_asset_hub.domain.models.ingress_telemetry_packet import (IngressTelemetryPacket,)
from energy_asset_hub.integrations.bess_api.uuid_packet_id_generator import (UuidPacketIdGenerator,)
from energy_asset_hub.integrations.bess_api.requests_http_client import (RequestsHttpClient,)


class HttpResponse(Protocol):
    def raise_for_status(self) -> None:
        ...

    def json(self) -> dict:
        ...


class HttpClient(Protocol):
    def get(self, url: str) -> HttpResponse:
        ...


class Clock(Protocol):
    def now_utc(self) -> datetime:
        ...


class PacketIdGenerator(Protocol):
    def next_id(self) -> str:
        ...


class BessRestTelemetryAdapter:
    def __init__(
        self,
        source_id: str,
        http_client: HttpClient | None = None,
        telemetry_url: str | None = None,
        clock: Clock | None = None,
        packet_id_generator: PacketIdGenerator | None = None,
    ):
        self._source_id = source_id
        self._http_client = (
            http_client
            if http_client is not None
            else RequestsHttpClient()
        )
        self._telemetry_url = telemetry_url
        self._clock = clock
        self._packet_id_generator = (
            packet_id_generator
            if packet_id_generator is not None
            else UuidPacketIdGenerator()
        )

    def create_packet(
        self,
        packet_id: str,
        payload: dict,
        received_at_utc: datetime,
    ) -> IngressTelemetryPacket:
        return IngressTelemetryPacket(
            packet_id=packet_id,
            source_id=self._source_id,
            ingress_payload=payload,
            received_at_utc=received_at_utc,
        )

    def fetch_packet(self) -> IngressTelemetryPacket:
        response = self._http_client.get(self._telemetry_url)

        response.raise_for_status()

        received_at_utc = self._clock.now_utc()
        payload = response.json()
        packet_id = self._packet_id_generator.next_id()

        return self.create_packet(
            packet_id=packet_id,
            payload=payload,
            received_at_utc=received_at_utc,
        )


