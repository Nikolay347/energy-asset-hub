from uuid import UUID

from energy_asset_hub.integrations.bess_api.uuid_packet_id_generator import (
    UuidPacketIdGenerator,
)


def test_generator_creates_uuid4_packet_id():
    generator = UuidPacketIdGenerator()

    packet_id = generator.next_id()

    parsed_uuid = UUID(packet_id)

    assert parsed_uuid.version == 4
    assert str(parsed_uuid) == packet_id



