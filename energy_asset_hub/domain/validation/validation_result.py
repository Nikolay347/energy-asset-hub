from dataclasses import dataclass

from energy_asset_hub.domain.validation.enums import IssueSeverity
from energy_asset_hub.domain.validation.validation_issue import ValidationIssue

@dataclass(frozen=True, slots=True)
class ValidationResult:
    """Stores all issues detected during a validation process"""
    issues: tuple[ValidationIssue, ...] = ()

    @property
    def is_valid(self) -> bool:
        """ Is there at least one error in this completed collection?"""
        for issue in self.issues:
            if issue.severity is IssueSeverity.ERROR:
                return False

        return True

    @property
    def has_warnings(self) -> bool:
        for issue in self.issues:
            if issue.severity is IssueSeverity.WARNING:
                return True

        return False



