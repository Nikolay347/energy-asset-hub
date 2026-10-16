import pytest
import sqlite3
from datetime import datetime, timezone

from energy_asset_hub.domain.models.ingress_telemetry_packet import (
    IngressTelemetryPacket,
)
from energy_asset_hub.infrastructure.persistence.sqlite.sqlite_telemetry_packet_repository import (
    SQLiteTelemetryPacketRepository,
)


def test_save_and_get_packet():
    connection = sqlite3.connect(":memory:")

    repository = SQLiteTelemetryPacketRepository(connection)

    packet = IngressTelemetryPacket(
        packet_id="packet-001",
        source_id="bess-api-01",
        ingress_payload={
            "timestamp": "2026-10-07T10:00:00+03:00",
            "soc_percent": 15.0,
            "power_kw": 70.0,
            "temperature_c": 25.0,
        },
        received_at_utc=datetime(
            2026,
            10,
            7,
            7,
            0,
            5,
            tzinfo=timezone.utc,
        ),
    )

    repository.save(packet)

    restored_packet = repository.get("packet-001")

    assert restored_packet == packet


def test_repository_allows_saving_same_packet_again():
    connection = sqlite3.connect(":memory:")

    repository = SQLiteTelemetryPacketRepository(connection)

    packet = IngressTelemetryPacket(
        packet_id="packet-001",
        source_id="bess-api-01",
        ingress_payload={
            "timestamp": "2026-10-07T10:00:00+03:00",
            "soc_percent": 15.0,
            "power_kw": 70.0,
            "temperature_c": 25.0,
        },
        received_at_utc=datetime(
            2026,
            10,
            7,
            7,
            0,
            5,
            tzinfo=timezone.utc,
        ),
    )

    repository.save(packet)
    repository.save(packet)

    restored_packet = repository.get("packet-001")

    assert restored_packet == packet


def test_repository_rejects_same_packet_id_with_different_data():
    connection = sqlite3.connect(":memory:")

    repository = SQLiteTelemetryPacketRepository(connection)

    original_packet = IngressTelemetryPacket(
        packet_id="packet-001",
        source_id="bess-api-01",
        ingress_payload={
            "timestamp": "2026-10-07T10:00:00+03:00",
            "soc_percent": 15.0,
            "power_kw": 70.0,
            "temperature_c": 25.0,
        },
        received_at_utc=datetime(
            2026,
            10,
            7,
            7,
            0,
            5,
            tzinfo=timezone.utc,
        ),
    )

    conflicting_packet = IngressTelemetryPacket(
        packet_id="packet-001",
        source_id="bess-api-01",
        ingress_payload={
            "timestamp": "2026-10-07T10:00:00+03:00",
            "soc_percent": 15.0,
            "power_kw": 80.0,
            "temperature_c": 25.0,
        },
        received_at_utc=datetime(
            2026,
            10,
            7,
            7,
            0,
            5,
            tzinfo=timezone.utc,
        ),
    )

    repository.save(original_packet)

    with pytest.raises(ValueError):
        repository.save(conflicting_packet)


def test_find_by_source_id_returns_only_matching_packets():
    connection = sqlite3.connect(":memory:")

    repository = SQLiteTelemetryPacketRepository(connection)

    first_packet = IngressTelemetryPacket(
        packet_id="packet-001",
        source_id="bess-api-01",
        ingress_payload={"soc_percent": 15.0},
        received_at_utc=datetime(
            2026,
            10,
            7,
            7,
            0,
            5,
            tzinfo=timezone.utc,
        ),
    )

    second_packet = IngressTelemetryPacket(
        packet_id="packet-002",
        source_id="bess-api-02",
        ingress_payload={"soc_percent": 20.0},
        received_at_utc=datetime(
            2026,
            10,
            7,
            7,
            1,
            5,
            tzinfo=timezone.utc,
        ),
    )

    third_packet = IngressTelemetryPacket(
        packet_id="packet-003",
        source_id="bess-api-01",
        ingress_payload={"soc_percent": 25.0},
        received_at_utc=datetime(
            2026,
            10,
            7,
            7,
            2,
            5,
            tzinfo=timezone.utc,
        ),
    )

    repository.save(first_packet)
    repository.save(second_packet)
    repository.save(third_packet)

    found_packets = repository.find_by_source_id("bess-api-01")

    assert found_packets == (
        first_packet,
        third_packet,
    )


def test_find_by_received_at_range_returns_only_packets_inside_range():
    connection = sqlite3.connect(":memory:")

    repository = SQLiteTelemetryPacketRepository(connection)

    first_packet = IngressTelemetryPacket(
        packet_id="packet-001",
        source_id="bess-api-01",
        ingress_payload={"soc_percent": 15.0},
        received_at_utc=datetime(
            2026, 10, 7, 7, 0, 0,
            tzinfo=timezone.utc,
        ),
    )

    second_packet = IngressTelemetryPacket(
        packet_id="packet-002",
        source_id="bess-api-01",
        ingress_payload={"soc_percent": 16.0},
        received_at_utc=datetime(
            2026, 10, 7, 7, 5, 0,
            tzinfo=timezone.utc,
        ),
    )

    third_packet = IngressTelemetryPacket(
        packet_id="packet-003",
        source_id="bess-api-01",
        ingress_payload={"soc_percent": 17.0},
        received_at_utc=datetime(
            2026, 10, 7, 7, 10, 0,
            tzinfo=timezone.utc,
        ),
    )

    repository.save(first_packet)
    repository.save(second_packet)
    repository.save(third_packet)

    found_packets = repository.find_by_received_at_range(
        start_utc=datetime(
            2026, 10, 7, 7, 2, 0,
            tzinfo=timezone.utc,
        ),
        end_utc=datetime(
            2026, 10, 7, 7, 10, 0,
            tzinfo=timezone.utc,
        ),
    )

    assert found_packets == (
        second_packet,
        third_packet,
    )


def test_find_by_received_at_range_rejects_invalid_range():
    connection = sqlite3.connect(":memory:")

    repository = SQLiteTelemetryPacketRepository(connection)

    start_utc = datetime(
        2026, 10, 7, 8, 0, 0,
        tzinfo=timezone.utc,
    )

    end_utc = datetime(
        2026, 10, 7, 7, 0, 0,
        tzinfo=timezone.utc,
    )

    with pytest.raises(ValueError):
        repository.find_by_received_at_range(
            start_utc=start_utc,
            end_utc=end_utc,
        )


def test_find_by_source_id_and_received_at_range_returns_only_matching_packets():
    connection = sqlite3.connect(":memory:")

    repository = SQLiteTelemetryPacketRepository(connection)

    first_packet = IngressTelemetryPacket(
        packet_id="packet-001",
        source_id="bess-api-01",
        ingress_payload={"soc_percent": 15.0},
        received_at_utc=datetime(
            2026, 10, 7, 7, 0, 0,
            tzinfo=timezone.utc,
        ),
    )

    second_packet = IngressTelemetryPacket(
        packet_id="packet-002",
        source_id="bess-api-02",
        ingress_payload={"soc_percent": 16.0},
        received_at_utc=datetime(
            2026, 10, 7, 7, 5, 0,
            tzinfo=timezone.utc,
        ),
    )

    third_packet = IngressTelemetryPacket(
        packet_id="packet-003",
        source_id="bess-api-01",
        ingress_payload={"soc_percent": 17.0},
        received_at_utc=datetime(
            2026, 10, 7, 7, 10, 0,
            tzinfo=timezone.utc,
        ),
    )

    fourth_packet = IngressTelemetryPacket(
        packet_id="packet-004",
        source_id="bess-api-01",
        ingress_payload={"soc_percent": 18.0},
        received_at_utc=datetime(
            2026, 10, 7, 7, 20, 0,
            tzinfo=timezone.utc,
        ),
    )

    repository.save(first_packet)
    repository.save(second_packet)
    repository.save(third_packet)
    repository.save(fourth_packet)

    found_packets = repository.find_by_source_id_and_received_at_range(
        source_id="bess-api-01",
        start_utc=datetime(
            2026, 10, 7, 7, 5, 0,
            tzinfo=timezone.utc,
        ),
        end_utc=datetime(
            2026, 10, 7, 7, 15, 0,
            tzinfo=timezone.utc,
        ),
    )

    assert found_packets == (
        third_packet,
    )


def test_find_by_source_id_and_received_at_range_rejects_invalid_range():
    connection = sqlite3.connect(":memory:")

    repository = SQLiteTelemetryPacketRepository(connection)

    start_utc = datetime(
        2026, 10, 7, 8, 0, 0,
        tzinfo=timezone.utc,
    )

    end_utc = datetime(
        2026, 10, 7, 7, 0, 0,
        tzinfo=timezone.utc,
    )

    with pytest.raises(ValueError):
        repository.find_by_source_id_and_received_at_range(
            source_id="bess-api-01",
            start_utc=start_utc,
            end_utc=end_utc,
        )