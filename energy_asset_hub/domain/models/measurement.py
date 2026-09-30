from dataclasses import dataclass
from datetime import datetime, timedelta
import math


@dataclass(frozen=True, slots=True)
class Measurement:
    asset_id: str
    source_id: str
    parameter_name: str
    value: float
    unit: str
    timestamp_utc: datetime


    def __post_init__(self):
        if (
                not isinstance(self.timestamp_utc, datetime)
                or self.timestamp_utc.utcoffset() != timedelta(0)
        ):
            raise ValueError(
                "timestamp_utc must be a timezone-aware UTC datetime"
            )

        if (
                not isinstance(self.timestamp_utc, datetime)
                or self.timestamp_utc.utcoffset() != timedelta(0)
        ):
            raise ValueError(
                "timestamp_utc must be a timezone-aware UTC datetime"
            )

        if (
                isinstance(self.value, bool)
                or not isinstance(self.value, (int, float))
        ):
            raise TypeError(
                "value must be an int or float, excluding bool"
            )

        if not math.isfinite(self.value):
            raise ValueError(
                "value must be a finite number"
            )

