from uuid import uuid4


class UuidPacketIdGenerator:
    def next_id(self) -> str:
        return str(uuid4())