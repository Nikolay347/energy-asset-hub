from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BessOperatingLimits:
    min_temperature_c: float
    max_temperature_c: float
    min_soc_percent: float
    max_soc_percent: float
    max_charge_power_kw: float
    max_discharge_power_kw: float

    def __post_init__(self):
        if self.min_temperature_c > self.max_temperature_c:
            raise ValueError(
                "min_temperature_c must not be greater than max_temperature_c"
            )

        if self.min_soc_percent > self.max_soc_percent:
            raise ValueError(
                "min_soc_percent must not be greater than max_soc_percent"
            )

        if self.min_soc_percent < 0:
            raise ValueError(
                "min_soc_percent must not be below 0"
            )

        if self.max_soc_percent > 100:
            raise ValueError(
                "max_soc_percent must not be above 100"
            )

        if self.max_charge_power_kw < 0:
            raise ValueError(
                "max_charge_power_kw must not be negative"
            )

        if self.max_discharge_power_kw < 0:
            raise ValueError(
                "max_discharge_power_kw must not be negative"
            )

