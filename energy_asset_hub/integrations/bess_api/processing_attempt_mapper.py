from datetime import datetime

from energy_asset_hub.domain.models.processing_attempt import (
    ProcessingAttempt,
    ProcessingStatus,
)


class BessProcessingAttemptMapper:
    def map(
        self,
        packet_id: str,
        processing_result,
        processed_at_utc: datetime,
        source_timezone_used: str | None,
    ) -> ProcessingAttempt:
        status = (
            ProcessingStatus.SUCCESS
            if processing_result.validation_result.is_valid
            else ProcessingStatus.FAILED
        )

        return ProcessingAttempt(
            packet_id=packet_id,
            processed_at_utc=processed_at_utc,
            status=status,
            diagnostics=processing_result.validation_result.issues,
            source_timezone_used=source_timezone_used,
        )