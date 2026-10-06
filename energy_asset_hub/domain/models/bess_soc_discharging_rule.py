from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BessSOCDischargingRule:
    full_power_soc_percent: float
    reduced_power_soc_percent: float
    reduced_power_fraction: float

    def __post_init__(self):
        if self.reduced_power_soc_percent >= self.full_power_soc_percent:
            raise ValueError(
                "reduced_power_soc_percent must be below full_power_soc_percent"
            )

        if self.reduced_power_fraction > 1.0:
            raise ValueError(
                "reduced_power_fraction must not be greater than 1.0"
            )

        if self.reduced_power_fraction < 0.0:
            raise ValueError(
                "reduced_power_fraction must not be below 0.0"
            )

        if self.reduced_power_soc_percent < 0.0:
            raise ValueError(
                "reduced_power_soc_percent must not be below 0.0"
            )

        if self.full_power_soc_percent > 100.0:
            raise ValueError(
                "full_power_soc_percent must not be above 100.0"
            )

    def allowed_discharge_fraction(
            self,
            soc_percent: float,
    ) -> float:
        if soc_percent >= self.full_power_soc_percent:
            return 1.0

        if soc_percent >= self.reduced_power_soc_percent:
            return self.reduced_power_fraction

        return 0.0



