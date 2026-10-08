import pytest
from datetime import datetime, timezone

from energy_asset_hub.domain.models.ingress_telemetry_packet import (
    IngressTelemetryPacket,
)


def test_ingress_telemetry_packet_stores_ingress_data():
    ingress_payload = {
        "asset_id": "BESS-01",
        "timestamp": "2026-10-01T12:00:00",
        "soc_percent": 72.5,
        "power_kw": -120.0,
        "temperature_c": 28.3,
    }

    received_at = datetime(
        2026, 10, 1, 9, 0, 8,
        tzinfo=timezone.utc,
    )

    packet = IngressTelemetryPacket(
        packet_id="PKT-0001",
        source_id="BESS-01-API",
        ingress_payload=ingress_payload,
        received_at_utc=received_at,
    )

    assert packet.packet_id == "PKT-0001"
    assert packet.source_id == "BESS-01-API"
    assert packet.ingress_payload == ingress_payload
    assert packet.received_at_utc == received_at


def test_ingress_packet_preserves_payload_snapshot():
    ingress_payload = {
        "asset_id": "BESS-01",
        "soc_percent": 72.5,
        "battery": {
            "temperature_c": 28.3,
        },
    }

    received_at = datetime(
        2026, 10, 1, 9, 0, 8,
        tzinfo=timezone.utc,
    )

    packet = IngressTelemetryPacket(
        packet_id="PKT-0002",
        source_id="BESS-01-API",
        ingress_payload=ingress_payload,
        received_at_utc=received_at,
    )

    # Змінюємо початковий словник після створення пакета.
    ingress_payload["soc_percent"] = 95.0
    ingress_payload["battery"]["temperature_c"] = 40.0

    # Збережений пакет повинен містити початкові значення.
    assert packet.ingress_payload["soc_percent"] == 72.5
    assert packet.ingress_payload["battery"]["temperature_c"] == 28.3


def test_ingress_packet_payload_cannot_be_modified():
    ingress_payload = {
        "asset_id": "BESS-01",
        "soc_percent": 72.5,
        "battery": {
            "temperature_c": 28.3,
        },
    }

    received_at = datetime(
        2026, 10, 1, 9, 0, 8,
        tzinfo=timezone.utc,
    )

    packet = IngressTelemetryPacket(
        packet_id="PKT-0003",
        source_id="BESS-01-API",
        ingress_payload=ingress_payload,
        received_at_utc=received_at,
    )

    with pytest.raises(TypeError):
        packet.ingress_payload["soc_percent"] = 95.0

    with pytest.raises(TypeError):
        packet.ingress_payload["battery"]["temperature_c"] = 40.0


def test_to_dict_returns_independent_mutable_copy():
    ingress_payload = {
        "asset_id": "BESS-01",
        "soc_percent": 72.5,
        "battery": {
            "temperature_c": 28.3,
        },
    }

    received_at = datetime(
        2026, 10, 1, 9, 0, 8,
        tzinfo=timezone.utc,
    )

    packet = IngressTelemetryPacket(
        packet_id="PKT-0004",
        source_id="BESS-01-API",
        ingress_payload=ingress_payload,
        received_at_utc=received_at,
    )

    restored_payload = packet.to_dict()

    assert restored_payload == ingress_payload

    restored_payload["soc_percent"] = 95.0
    restored_payload["battery"]["temperature_c"] = 40.0

    assert packet.ingress_payload["soc_percent"] == 72.5
    assert packet.ingress_payload["battery"]["temperature_c"] == 28.3


def test_to_dict_returns_independent_copies():
    ingress_payload = {
        "asset_id": "BESS-01",
        "soc_percent": 72.5,
        "battery": {
            "temperature_c": 28.3,
        },
    }

    received_at = datetime(
        2026, 10, 1, 9, 0, 8,
        tzinfo=timezone.utc,
    )

    packet = IngressTelemetryPacket(
        packet_id="PKT-0005",
        source_id="BESS-01-API",
        ingress_payload=ingress_payload,
        received_at_utc=received_at,
    )

    payload_1 = packet.to_dict()
    payload_2 = packet.to_dict()

    payload_1["soc_percent"] = 95.0
    payload_1["battery"]["temperature_c"] = 40.0

    assert payload_2["soc_percent"] == 72.5
    assert payload_2["battery"]["temperature_c"] == 28.3

    assert packet.ingress_payload["soc_percent"] == 72.5
    assert packet.ingress_payload["battery"]["temperature_c"] == 28.3


def test_freeze_and_defrost_preserve_payload_data():
    ingress_payload = {
        "asset_id": "BESS-01",
        "soc_percent": 72.5,
        "battery": {
            "temperature_c": 28.3,
        },
    }

    received_at = datetime(
        2026, 10, 1, 9, 0, 8,
        tzinfo=timezone.utc,
    )

    packet = IngressTelemetryPacket(
        packet_id="PKT-0006",
        source_id="BESS-01-API",
        ingress_payload=ingress_payload,
        received_at_utc=received_at,
    )

    restored_payload = packet.to_dict()

    assert restored_payload == ingress_payload

    assert restored_payload is not ingress_payload
    assert restored_payload["battery"] is not ingress_payload["battery"]






