from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfoNotFoundError

from energy_asset_hub.domain.validation.validation_result import (
    ValidationResult,
)
from energy_asset_hub.domain.time.timestamp_normalizer import (
    TimestampNormalizer,
    TimezoneRequiredError,
    AmbiguousLocalTimeError,
    NonexistentLocalTimeError,
)

from energy_asset_hub.integrations.bess_api.payload_validator import (
    BessTelemetryPayloadValidator,
)
from energy_asset_hub.domain.validation.enums import (
    IssueSeverity, ValidationIssueCode,
)

from energy_asset_hub.domain.validation.validation_issue import (
    ValidationIssue,
)


@dataclass(frozen=True, slots=True)
class ValidatedBessPayload:
    asset_id: str
    raw_timestamp: str
    soc_percent: float
    power_kw: float
    temperature_c: float


@dataclass(frozen=True, slots=True)
class BessTelemetryProcessingResult:
    """Stores the outcome of BESS telemetry processing."""

    validation_result: ValidationResult
    timestamp_utc: datetime | None
    validated_payload: ValidatedBessPayload | None = None


class BessTelemetryProcessor:
    """Coordinates BESS payload validation and time normalization."""
    _ERROR_MAPPING = {
        TimezoneRequiredError: (
            ValidationIssueCode.TIMEZONE_REQUIRED,
            "timestamp",
            "Timestamp with timezone or configured source timezone",
        ),
        AmbiguousLocalTimeError: (
            ValidationIssueCode.AMBIGUOUS_LOCAL_TIME,
            "timestamp",
            "Unambiguous local timestamp",
        ),
        NonexistentLocalTimeError: (
            ValidationIssueCode.NONEXISTENT_LOCAL_TIME,
            "timestamp",
            "Existing local timestamp",
        ),
        ZoneInfoNotFoundError: (
            ValidationIssueCode.INVALID_SOURCE_TIMEZONE,
            "source_timezone",
            "Valid IANA timezone identifier",
        ),
    }

    def __init__(self):
        self._validator = BessTelemetryPayloadValidator()
        self._normalizer = TimestampNormalizer()

    def process(
        self,
        data: dict,
        source_timezone: str | None = None,
    ) -> BessTelemetryProcessingResult:

        validation_result = self._validator.validate(data)

        if not validation_result.is_valid:
            return BessTelemetryProcessingResult(
                validation_result=validation_result,
                timestamp_utc=None,
            )

        try:
            timestamp_utc = self._normalizer.normalize(
                data["timestamp"],
                source_timezone=source_timezone,
            )
        except (
                TimezoneRequiredError,
                AmbiguousLocalTimeError,
                NonexistentLocalTimeError,
                ZoneInfoNotFoundError,
        ) as exc:

            issue_code, field_name, expected = self._ERROR_MAPPING[type(exc)]

            actual_value = (
                source_timezone
                if field_name == "source_timezone"
                else data["timestamp"]
            )

            issue = ValidationIssue(
                field_name=field_name,
                code=issue_code,
                severity=IssueSeverity.ERROR,
                message=str(exc),
                actual_value=actual_value,
                expected=expected,
            )

            validation_result = ValidationResult(
                issues=validation_result.issues + (issue,)
            )

            return BessTelemetryProcessingResult(
                validation_result=validation_result,
                timestamp_utc=None,
            )

#
        validated_payload = ValidatedBessPayload(
            asset_id=data["asset_id"],
            raw_timestamp=data["timestamp"],
            soc_percent=data["soc_percent"],
            power_kw=data["power_kw"],
            temperature_c=data["temperature_c"],
        )


        return BessTelemetryProcessingResult(
            validation_result=validation_result,
            timestamp_utc=timestamp_utc,
            validated_payload=validated_payload,
        )