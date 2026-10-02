import pytest
from datetime import datetime, timezone

from energy_asset_hub.domain.models.normalized_telemetry_packet import (
    NormalizedTelemetryPacket,
)


def test_normalized_telemetry_packet_stores_normalized_data():
    normalized_payload = {
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

    packet = NormalizedTelemetryPacket(
        packet_id="PKT-0001",
        source_id="BESS-01-API",
        normalized_payload=normalized_payload,
        received_at_utc=received_at,
    )

    assert packet.packet_id == "PKT-0001"
    assert packet.source_id == "BESS-01-API"
    assert packet.normalized_payload == normalized_payload
    assert packet.received_at_utc == received_at


def test_normalized_packet_preserves_payload_snapshot():
    normalized_payload = {
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

    packet = NormalizedTelemetryPacket(
        packet_id="PKT-0002",
        source_id="BESS-01-API",
        normalized_payload=normalized_payload,
        received_at_utc=received_at,
    )

    # Змінюємо початковий словник після створення пакета.
    normalized_payload["soc_percent"] = 95.0
    normalized_payload["battery"]["temperature_c"] = 40.0

    # Збережений пакет повинен містити початкові значення.
    assert packet.normalized_payload["soc_percent"] == 72.5
    assert packet.normalized_payload["battery"]["temperature_c"] == 28.3


def test_normalized_packet_payload_cannot_be_modified():
    normalized_payload = {
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

    packet = NormalizedTelemetryPacket(
        packet_id="PKT-0003",
        source_id="BESS-01-API",
        normalized_payload=normalized_payload,
        received_at_utc=received_at,
    )

    with pytest.raises(TypeError):
        packet.normalized_payload["soc_percent"] = 95.0

    with pytest.raises(TypeError):
        packet.normalized_payload["battery"]["temperature_c"] = 40.0


def test_to_dict_returns_independent_mutable_copy():
    normalized_payload = {
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

    packet = NormalizedTelemetryPacket(
        packet_id="PKT-0004",
        source_id="BESS-01-API",
        normalized_payload=normalized_payload,
        received_at_utc=received_at,
    )

    restored_payload = packet.to_dict()

    assert restored_payload == normalized_payload

    restored_payload["soc_percent"] = 95.0
    restored_payload["battery"]["temperature_c"] = 40.0

    assert packet.normalized_payload["soc_percent"] == 72.5
    assert packet.normalized_payload["battery"]["temperature_c"] == 28.3


def test_to_dict_returns_independent_copies():
    normalized_payload = {
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

    packet = NormalizedTelemetryPacket(
        packet_id="PKT-0005",
        source_id="BESS-01-API",
        normalized_payload=normalized_payload,
        received_at_utc=received_at,
    )

    payload_1 = packet.to_dict()
    payload_2 = packet.to_dict()

    payload_1["soc_percent"] = 95.0
    payload_1["battery"]["temperature_c"] = 40.0

    assert payload_2["soc_percent"] == 72.5
    assert payload_2["battery"]["temperature_c"] == 28.3

    assert packet.normalized_payload["soc_percent"] == 72.5
    assert packet.normalized_payload["battery"]["temperature_c"] == 28.3


def test_freeze_and_defrost_preserve_payload_data():
    normalized_payload = {
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

    packet = NormalizedTelemetryPacket(
        packet_id="PKT-0006",
        source_id="BESS-01-API",
        normalized_payload=normalized_payload,
        received_at_utc=received_at,
    )

    restored_payload = packet.to_dict()

    assert restored_payload == normalized_payload

    assert restored_payload is not normalized_payload
    assert restored_payload["battery"] is not normalized_payload["battery"]






