from dataclasses import dataclass
from datetime import datetime
from types import MappingProxyType


def _freeze(value):
    if isinstance(value, dict):
        return MappingProxyType({
            key: _freeze(item)
            for key, item in value.items()
        })

    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)

    return value


def _defrost(value):
    if isinstance(value, MappingProxyType):
        return {
            key: _defrost(item)
            for key, item in value.items()
        }

    if isinstance(value, tuple):
        return [_defrost(item) for item in value]

    return value


@dataclass(frozen=True, slots=True)
class IngressTelemetryPacket:
    packet_id: str
    source_id: str
    ingress_payload: dict
    received_at_utc: datetime

    def __post_init__(self):
        object.__setattr__(
            self,
            "ingress_payload",
            _freeze(self.ingress_payload),
        )

    def to_dict(self) -> dict:
        return _defrost(self.ingress_payload)



