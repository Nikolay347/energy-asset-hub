import pytest
from datetime import datetime, timezone

from energy_asset_hub.domain.models.normalized_telemetry_packet import (
    NormalizedTelemetryPacket,
)
from energy_asset_hub.domain.repositories.normalized_telemetry_packet_repository import (
    InMemoryNormalizedTelemetryPacketRepository,
)


def test_repository_saves_and_returns_packet_by_id():
    packet = NormalizedTelemetryPacket(
        packet_id="PKT-0007",
        source_id="BESS-01-API",
        normalized_payload={
            "asset_id": "BESS-01",
            "timestamp": "2026-10-02T12:30:00",
            "soc_percent": 72.5,
            "power_kw": -120.0,
            "temperature_c": 28.3,
        },
        received_at_utc=datetime(
            2026, 10, 2, 9, 30, 5,
            tzinfo=timezone.utc,
        ),
    )

    repository = InMemoryNormalizedTelemetryPacketRepository()

    repository.save(packet)

    restored_packet = repository.get("PKT-0007")

    assert restored_packet == packet


def test_repository_returns_none_when_packet_is_not_found():
    repository = InMemoryNormalizedTelemetryPacketRepository()

    packet = repository.get("UNKNOWN-PACKET")

    assert packet is None


def test_repository_rejects_different_packet_with_existing_packet_id():
    first_packet = NormalizedTelemetryPacket(
        packet_id="PKT-0007",
        source_id="BESS-01-API",
        normalized_payload={
            "asset_id": "BESS-01",
            "timestamp": "2026-10-02T12:30:00",
            "soc_percent": 72.5,
            "power_kw": -120.0,
            "temperature_c": 28.3,
        },
        received_at_utc=datetime(
            2026, 10, 2, 9, 30, 5,
            tzinfo=timezone.utc,
        ),
    )

    conflicting_packet = NormalizedTelemetryPacket(
        packet_id="PKT-0007",
        source_id="BESS-01-API",
        normalized_payload={
            "asset_id": "BESS-01",
            "timestamp": "2026-10-02T12:30:00",
            "soc_percent": 81.0,
            "power_kw": -95.0,
            "temperature_c": 29.1,
        },
        received_at_utc=datetime(
            2026, 10, 2, 9, 30, 7,
            tzinfo=timezone.utc,
        ),
    )

    repository = InMemoryNormalizedTelemetryPacketRepository()

    repository.save(first_packet)

    with pytest.raises(ValueError):
        repository.save(conflicting_packet)


def test_repository_allows_saving_same_packet_again():
    packet = NormalizedTelemetryPacket(
        packet_id="PKT-0007",
        source_id="BESS-01-API",
        normalized_payload={
            "asset_id": "BESS-01",
            "timestamp": "2026-10-02T12:30:00",
            "soc_percent": 72.5,
            "power_kw": -120.0,
            "temperature_c": 28.3,
        },
        received_at_utc=datetime(
            2026, 10, 2, 9, 30, 5,
            tzinfo=timezone.utc,
        ),
    )

    repository = InMemoryNormalizedTelemetryPacketRepository()

    repository.save(packet)
    repository.save(packet)

    restored_packet = repository.get("PKT-0007")

    assert restored_packet == packet


def test_repository_allows_equivalent_packet_with_same_packet_id():
    first_packet = NormalizedTelemetryPacket(
        packet_id="PKT-0007",
        source_id="BESS-01-API",
        normalized_payload={
            "asset_id": "BESS-01",
            "timestamp": "2026-10-02T12:30:00",
            "soc_percent": 72.5,
            "power_kw": -120.0,
            "temperature_c": 28.3,
        },
        received_at_utc=datetime(
            2026, 10, 2, 9, 30, 5,
            tzinfo=timezone.utc,
        ),
    )

    second_packet = NormalizedTelemetryPacket(
        packet_id="PKT-0007",
        source_id="BESS-01-API",
        normalized_payload={
            "asset_id": "BESS-01",
            "timestamp": "2026-10-02T12:30:00",
            "soc_percent": 72.5,
            "power_kw": -120.0,
            "temperature_c": 28.3,
        },
        received_at_utc=datetime(
            2026, 10, 2, 9, 30, 5,
            tzinfo=timezone.utc,
        ),
    )

    assert first_packet is not second_packet
    assert first_packet == second_packet

    repository = InMemoryNormalizedTelemetryPacketRepository()

    repository.save(first_packet)
    repository.save(second_packet)

    restored_packet = repository.get("PKT-0007")

    assert restored_packet == first_packet


def test_repository_returns_packets_for_source_id():
    repository = InMemoryNormalizedTelemetryPacketRepository()

    packet_1 = NormalizedTelemetryPacket(
        packet_id="PKT-0001",
        source_id="BESS-01-API",
        normalized_payload={
            "asset_id": "BESS-01",
            "timestamp": "2026-10-02T12:30:00",
            "soc_percent": 72.5,
            "power_kw": -120.0,
            "temperature_c": 28.3,
        },
        received_at_utc=datetime(
            2026, 10, 2, 9, 30, 5,
            tzinfo=timezone.utc,
        ),
    )

    packet_2 = NormalizedTelemetryPacket(
        packet_id="PKT-0002",
        source_id="BESS-02-API",
        normalized_payload={
            "asset_id": "BESS-02",
            "timestamp": "2026-10-02T12:31:00",
            "soc_percent": 64.0,
            "power_kw": -80.0,
            "temperature_c": 27.5,
        },
        received_at_utc=datetime(
            2026, 10, 2, 9, 31, 5,
            tzinfo=timezone.utc,
        ),
    )

    packet_3 = NormalizedTelemetryPacket(
        packet_id="PKT-0003",
        source_id="BESS-01-API",
        normalized_payload={
            "asset_id": "BESS-01",
            "timestamp": "2026-10-02T12:32:00",
            "soc_percent": 71.8,
            "power_kw": -110.0,
            "temperature_c": 28.5,
        },
        received_at_utc=datetime(
            2026, 10, 2, 9, 32, 5,
            tzinfo=timezone.utc,
        ),
    )

    repository.save(packet_1)
    repository.save(packet_2)
    repository.save(packet_3)

    packets = repository.find_by_source_id("BESS-01-API")

    assert packets == (packet_1, packet_3)


def test_repository_returns_empty_tuple_when_source_id_is_not_found():
    repository = InMemoryNormalizedTelemetryPacketRepository()

    packets = repository.find_by_source_id("UNKNOWN-SOURCE")

    assert packets == ()


def test_repository_returns_packets_received_in_time_range():
    repository = InMemoryNormalizedTelemetryPacketRepository()

    packet_1 = NormalizedTelemetryPacket(
        packet_id="PKT-0001",
        source_id="BESS-01-API",
        normalized_payload={"asset_id": "BESS-01"},
        received_at_utc=datetime(
            2026, 10, 2, 9, 30, 0,
            tzinfo=timezone.utc,
        ),
    )

    packet_2 = NormalizedTelemetryPacket(
        packet_id="PKT-0002",
        source_id="BESS-01-API",
        normalized_payload={"asset_id": "BESS-01"},
        received_at_utc=datetime(
            2026, 10, 2, 10, 0, 0,
            tzinfo=timezone.utc,
        ),
    )

    packet_3 = NormalizedTelemetryPacket(
        packet_id="PKT-0003",
        source_id="BESS-01-API",
        normalized_payload={"asset_id": "BESS-01"},
        received_at_utc=datetime(
            2026, 10, 2, 10, 30, 0,
            tzinfo=timezone.utc,
        ),
    )

    repository.save(packet_1)
    repository.save(packet_2)
    repository.save(packet_3)

    packets = repository.find_by_received_at_range(
        start_utc=datetime(
            2026, 10, 2, 9, 45, 0,
            tzinfo=timezone.utc,
        ),
        end_utc=datetime(
            2026, 10, 2, 10, 15, 0,
            tzinfo=timezone.utc,
        ),
    )

    assert packets == (packet_2,)


def test_repository_time_range_includes_boundary_packets():
    repository = InMemoryNormalizedTelemetryPacketRepository()

    packet_start = NormalizedTelemetryPacket(
        packet_id="PKT-START",
        source_id="BESS-01-API",
        normalized_payload={"asset_id": "BESS-01"},
        received_at_utc=datetime(
            2026, 10, 2, 10, 0, 0,
            tzinfo=timezone.utc,
        ),
    )

    packet_end = NormalizedTelemetryPacket(
        packet_id="PKT-END",
        source_id="BESS-01-API",
        normalized_payload={"asset_id": "BESS-01"},
        received_at_utc=datetime(
            2026, 10, 2, 11, 0, 0,
            tzinfo=timezone.utc,
        ),
    )

    repository.save(packet_start)
    repository.save(packet_end)

    packets = repository.find_by_received_at_range(
        start_utc=datetime(
            2026, 10, 2, 10, 0, 0,
            tzinfo=timezone.utc,
        ),
        end_utc=datetime(
            2026, 10, 2, 11, 0, 0,
            tzinfo=timezone.utc,
        ),
    )

    assert packets == (packet_start, packet_end)


def test_repository_rejects_invalid_time_range():
    repository = InMemoryNormalizedTelemetryPacketRepository()

    with pytest.raises(ValueError):
        repository.find_by_received_at_range(
            start_utc=datetime(
                2026, 10, 2, 11, 0, 0,
                tzinfo=timezone.utc,
            ),
            end_utc=datetime(
                2026, 10, 2, 10, 0, 0,
                tzinfo=timezone.utc,
            ),
        )

def test_repository_returns_packets_for_source_id_and_time_range():
    repository = InMemoryNormalizedTelemetryPacketRepository()

    packet_1 = NormalizedTelemetryPacket(
        packet_id="PKT-0001",
        source_id="BESS-01-API",
        normalized_payload={"asset_id": "BESS-01"},
        received_at_utc=datetime(
            2026, 10, 2, 9, 30, 0,
            tzinfo=timezone.utc,
        ),
    )

    packet_2 = NormalizedTelemetryPacket(
        packet_id="PKT-0002",
        source_id="BESS-01-API",
        normalized_payload={"asset_id": "BESS-01"},
        received_at_utc=datetime(
            2026, 10, 2, 10, 0, 0,
            tzinfo=timezone.utc,
        ),
    )

    packet_3 = NormalizedTelemetryPacket(
        packet_id="PKT-0003",
        source_id="BESS-02-API",
        normalized_payload={"asset_id": "BESS-02"},
        received_at_utc=datetime(
            2026, 10, 2, 10, 5, 0,
            tzinfo=timezone.utc,
        ),
    )

    packet_4 = NormalizedTelemetryPacket(
        packet_id="PKT-0004",
        source_id="BESS-01-API",
        normalized_payload={"asset_id": "BESS-01"},
        received_at_utc=datetime(
            2026, 10, 2, 11, 0, 0,
            tzinfo=timezone.utc,
        ),
    )

    repository.save(packet_1)
    repository.save(packet_2)
    repository.save(packet_3)
    repository.save(packet_4)

    packets = repository.find_by_source_id_and_received_at_range(
        source_id="BESS-01-API",
        start_utc=datetime(
            2026, 10, 2, 9, 45, 0,
            tzinfo=timezone.utc,
        ),
        end_utc=datetime(
            2026, 10, 2, 10, 15, 0,
            tzinfo=timezone.utc,
        ),
    )

    assert packets == (packet_2,)


def test_repository_source_and_time_range_rejects_invalid_time_range():
    repository = InMemoryNormalizedTelemetryPacketRepository()

    with pytest.raises(ValueError):
        repository.find_by_source_id_and_received_at_range(
            source_id="BESS-01-API",
            start_utc=datetime(
                2026, 10, 2, 11, 0, 0,
                tzinfo=timezone.utc,
            ),
            end_utc=datetime(
                2026, 10, 2, 10, 0, 0,
                tzinfo=timezone.utc,
            ),
        )


def test_repository_returns_source_packets_sorted_by_received_at():
    repository = InMemoryNormalizedTelemetryPacketRepository()

    packet_late = NormalizedTelemetryPacket(
        packet_id="PKT-LATE",
        source_id="BESS-01-API",
        normalized_payload={"asset_id": "BESS-01"},
        received_at_utc=datetime(
            2026, 10, 2, 11, 0, 0,
            tzinfo=timezone.utc,
        ),
    )

    packet_early = NormalizedTelemetryPacket(
        packet_id="PKT-EARLY",
        source_id="BESS-01-API",
        normalized_payload={"asset_id": "BESS-01"},
        received_at_utc=datetime(
            2026, 10, 2, 9, 0, 0,
            tzinfo=timezone.utc,
        ),
    )

    packet_middle = NormalizedTelemetryPacket(
        packet_id="PKT-MIDDLE",
        source_id="BESS-01-API",
        normalized_payload={"asset_id": "BESS-01"},
        received_at_utc=datetime(
            2026, 10, 2, 10, 0, 0,
            tzinfo=timezone.utc,
        ),
    )

    repository.save(packet_late)
    repository.save(packet_early)
    repository.save(packet_middle)

    packets = repository.find_by_source_id("BESS-01-API")

    assert packets == (
        packet_early,
        packet_middle,
        packet_late,
    )


def test_repository_time_range_returns_packets_sorted_by_received_at():
    repository = InMemoryNormalizedTelemetryPacketRepository()

    packet_late = NormalizedTelemetryPacket(
        packet_id="PKT-LATE",
        source_id="BESS-01-API",
        normalized_payload={"asset_id": "BESS-01"},
        received_at_utc=datetime(
            2026, 10, 2, 10, 30, 0,
            tzinfo=timezone.utc,
        ),
    )

    packet_early = NormalizedTelemetryPacket(
        packet_id="PKT-EARLY",
        source_id="BESS-01-API",
        normalized_payload={"asset_id": "BESS-01"},
        received_at_utc=datetime(
            2026, 10, 2, 9, 30, 0,
            tzinfo=timezone.utc,
        ),
    )

    packet_middle = NormalizedTelemetryPacket(
        packet_id="PKT-MIDDLE",
        source_id="BESS-01-API",
        normalized_payload={"asset_id": "BESS-01"},
        received_at_utc=datetime(
            2026, 10, 2, 10, 0, 0,
            tzinfo=timezone.utc,
        ),
    )

    repository.save(packet_late)
    repository.save(packet_early)
    repository.save(packet_middle)

    packets = repository.find_by_received_at_range(
        start_utc=datetime(
            2026, 10, 2, 9, 0, 0,
            tzinfo=timezone.utc,
        ),
        end_utc=datetime(
            2026, 10, 2, 11, 0, 0,
            tzinfo=timezone.utc,
        ),
    )

    assert packets == (
        packet_early,
        packet_middle,
        packet_late,
    )


