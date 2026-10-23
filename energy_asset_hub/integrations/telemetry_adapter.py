from typing import Protocol

from energy_asset_hub.domain.models.ingress_telemetry_packet import (
    IngressTelemetryPacket,
)


class TelemetryAdapter(Protocol):
    def fetch_packet(self) -> IngressTelemetryPacket:
        ...




