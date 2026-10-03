from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from energy_asset_hub.domain.validation.validation_issue import ValidationIssue

class ProcessingStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class ProcessingAttempt:
    packet_id: str
    processed_at_utc: datetime
    status: ProcessingStatus
    diagnostics: tuple[ValidationIssue, ...] = ()
    source_timezone_used: str | None = None