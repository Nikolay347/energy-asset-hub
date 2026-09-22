from dataclasses import dataclass
from energy_asset_hub.domain.validation.enums import (IssueSeverity, ValidationIssueCode)


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    """ Describes one problem detected during data validation.
        It only stores the description of one already detected problem
    """

    field_name: str | None
    code: ValidationIssueCode
    severity: IssueSeverity
    message: str
    actual_value: object | None = None
    expected: str | None = None