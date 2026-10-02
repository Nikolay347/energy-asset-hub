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


