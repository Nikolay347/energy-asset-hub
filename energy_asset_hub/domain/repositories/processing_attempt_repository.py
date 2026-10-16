from typing import Protocol

from energy_asset_hub.domain.models.processing_attempt import ProcessingAttempt


class ProcessingAttemptRepository(Protocol):
    def save(self, attempt: ProcessingAttempt) -> None:
        ...

    def get(
        self,
        packet_id: str,
        attempt_number: int,
    ) -> ProcessingAttempt | None:
        ...

    def get_latest_attempt_number(
        self,
        packet_id: str,
    ) -> int | None:
        ...