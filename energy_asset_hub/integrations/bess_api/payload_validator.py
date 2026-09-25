from energy_asset_hub.domain.validation.enums import (
    IssueSeverity,
    ValidationIssueCode,
)
from energy_asset_hub.domain.validation.validation_issue import ValidationIssue
from energy_asset_hub.domain.validation.validation_result import ValidationResult


class BessTelemetryPayloadValidator:
    """Validates the structure, field types, and values of a BESS API payload."""
    _REQUIRED_FIELDS: dict[str, tuple[type, ...]] = {
        "asset_id": (str,),
        "timestamp": (str,),
        "soc_percent": (int, float),
        "power_kw": (int, float),
        "temperature_c": (int, float),
    }

    def validate(self, data: object) -> ValidationResult:
        issues: list[ValidationIssue] = []

        if not isinstance(data, dict):
            issues.append(
                ValidationIssue(
                    field_name=None,
                    code=ValidationIssueCode.INVALID_TYPE,
                    severity=IssueSeverity.ERROR,
                    message="The API payload must be a JSON object",
                    actual_value=data,
                    expected="dict",
                )
            )

            return ValidationResult(
                issues=tuple(issues),
            )

        for field_name, expected_types in self._REQUIRED_FIELDS.items():
            if field_name not in data:
                issues.append(
                    ValidationIssue(
                        field_name=field_name,
                        code=ValidationIssueCode.MISSING_FIELD,
                        severity=IssueSeverity.ERROR,
                        message=f"Required field {field_name} is missing",
                        expected=self._format_expected_types(expected_types),
                    )
                )
                continue

            actual_value = data[field_name]

            if not self._matches_expected_type(
                actual_value,
                expected_types,
            ):
                issues.append(
                    ValidationIssue(
                        field_name=field_name,
                        code=ValidationIssueCode.INVALID_TYPE,
                        severity=IssueSeverity.ERROR,
                        message=f"Field {field_name} has an invalid type",
                        actual_value=actual_value,
                        expected=self._format_expected_types(expected_types),
                    )
                )
                continue

            if field_name == "soc_percent" and not 0 <= actual_value <= 100:
                issues.append(
                    ValidationIssue(
                        field_name="soc_percent",
                        code=ValidationIssueCode.VALUE_OUT_OF_RANGE,
                        severity=IssueSeverity.ERROR,
                        message="Field soc_percent is outside the allowed range",
                        actual_value=actual_value,
                        expected="0 <= soc_percent <= 100",
                    )
                )

        return ValidationResult(
            issues=tuple(issues),
        )

    @staticmethod
    def _matches_expected_type(
            value: object,
            expected_types: tuple[type, ...],
    ) -> bool:
        if isinstance(value, bool) and bool not in expected_types:
            return False

        return isinstance(value, expected_types)

    @staticmethod
    def _format_expected_types(
            expected_types: tuple[type, ...],
    ) -> str:
        return " or ".join(
            expected_type.__name__
            for expected_type in expected_types
        )