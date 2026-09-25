from enum import Enum


# Creating enumeration classes
class IssueSeverity(Enum):
    """
    The class defines the list of permitted severity levels
    WARNING -
    ERROR -
    """
    WARNING = "warning"
    ERROR = "error"

class ValidationIssueCode(Enum):
    MISSING_FIELD = (1001, "missing_field")
    INVALID_TYPE = (1002, "invalid_type")
    VALUE_OUT_OF_RANGE = (2001, "value_out_of_range")
    UNIT_MISMATCH = (2002, "unit_mismatch")
    STALE_DATA = (3001, "stale_data")
    FUTURE_TIMESTAMP = (3002, "future_timestamp")

    def __init__(
            self,
            numeric_code: int,
            string_code: str,
    ) -> None:
        self.numeric_code = numeric_code
        self.string_code = string_code

