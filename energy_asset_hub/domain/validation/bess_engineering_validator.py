from energy_asset_hub.domain.models.bess_operating_limits import (
    BessOperatingLimits,
)
from energy_asset_hub.domain.validation.enums import (
    IssueSeverity,
    ValidationIssueCode,
)
from energy_asset_hub.domain.validation.validation_issue import (
    ValidationIssue,
)
from energy_asset_hub.domain.validation.validation_result import (
    ValidationResult,
)
from energy_asset_hub.domain.models.bess_soc_discharging_rule import (
    BessSOCDischargingRule,
)


class BessEngineeringValidator:
    def validate_operating_conditions(
        self,
        temperature_c: float,
        soc_percent: float,
        power_kw: float,
        limits: BessOperatingLimits,
        soc_discharging_rule: BessSOCDischargingRule | None = None,
    ) -> ValidationResult:
        issues: list[ValidationIssue] = []

        if temperature_c > limits.max_temperature_c:
            issues.append(
                ValidationIssue(
                    field_name="temperature_c",
                    code=ValidationIssueCode.VALUE_OUT_OF_RANGE,
                    severity=IssueSeverity.ERROR,
                    message="BESS temperature exceeds the configured maximum",
                    actual_value=temperature_c,
                    expected=(
                        f"temperature_c <= {limits.max_temperature_c}"
                    ),
                )
            )

        if temperature_c < limits.min_temperature_c:
            issues.append(
                ValidationIssue(
                    field_name="temperature_c",
                    code=ValidationIssueCode.VALUE_OUT_OF_RANGE,
                    severity=IssueSeverity.ERROR,
                    message="BESS temperature is below the configured minimum",
                    actual_value=temperature_c,
                    expected=(
                        f"temperature_c >= {limits.min_temperature_c}"
                    ),
                )
            )

        if soc_percent < limits.min_soc_percent:
            issues.append(
                ValidationIssue(
                    field_name="soc_percent",
                    code=ValidationIssueCode.VALUE_OUT_OF_RANGE,
                    severity=IssueSeverity.ERROR,
                    message="BESS SOC is below the configured minimum",
                    actual_value=soc_percent,
                    expected=f"soc_percent >= {limits.min_soc_percent}",
                )
            )

        if soc_percent > limits.max_soc_percent:
            issues.append(
                ValidationIssue(
                    field_name="soc_percent",
                    code=ValidationIssueCode.VALUE_OUT_OF_RANGE,
                    severity=IssueSeverity.ERROR,
                    message="BESS SOC exceeds the configured maximum",
                    actual_value=soc_percent,
                    expected=f"soc_percent <= {limits.max_soc_percent}",
                )
            )

        effective_max_discharge_power_kw = limits.max_discharge_power_kw

        if soc_discharging_rule is not None:
            discharge_fraction = soc_discharging_rule.allowed_discharge_fraction(
                soc_percent=soc_percent,
            )

            effective_max_discharge_power_kw = (
                    limits.max_discharge_power_kw * discharge_fraction
            )


        if power_kw > effective_max_discharge_power_kw:
            issues.append(
                ValidationIssue(
                    field_name="power_kw",
                    code=ValidationIssueCode.VALUE_OUT_OF_RANGE,
                    severity=IssueSeverity.ERROR,
                    message="BESS discharge power exceeds the configured maximum",
                    actual_value=power_kw,
                    expected=f"power_kw <= {effective_max_discharge_power_kw}",
                )
            )

        if power_kw < -limits.max_charge_power_kw:
            issues.append(
                ValidationIssue(
                    field_name="power_kw",
                    code=ValidationIssueCode.VALUE_OUT_OF_RANGE,
                    severity=IssueSeverity.ERROR,
                    message="BESS charge power exceeds the configured maximum",
                    actual_value=power_kw,
                    expected=f"power_kw >= {-limits.max_charge_power_kw}",
                )
            )


        return ValidationResult(
            issues=tuple(issues),
        )