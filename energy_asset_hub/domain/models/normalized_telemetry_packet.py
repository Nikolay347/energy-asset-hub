from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class NormalizedTelemetryPacket:
    packet_id: str
    source_id: str
    normalized_payload: dict
    received_at_utc: datetime

    def __post_init__(self):
        object.__setattr__(
            self,
            "normalized_payload",
            deepcopy(self.normalized_payload),
        )

