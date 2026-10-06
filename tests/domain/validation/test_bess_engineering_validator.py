from energy_asset_hub.domain.models.bess_operating_limits import (
    BessOperatingLimits,
)
from energy_asset_hub.domain.validation.bess_engineering_validator import (
    BessEngineeringValidator,
)
from energy_asset_hub.domain.validation.enums import (
    IssueSeverity,
    ValidationIssueCode,
)
from energy_asset_hub.domain.models.bess_soc_discharging_rule import (
    BessSOCDischargingRule,
)


def test_validator_reports_temperature_above_maximum():
    limits = BessOperatingLimits(
        min_temperature_c=-20.0,
        max_temperature_c=55.0,
        min_soc_percent=10.0,
        max_soc_percent=95.0,
        max_charge_power_kw=100.0,
        max_discharge_power_kw=120.0,
    )

    validator = BessEngineeringValidator()

    result = validator.validate_operating_conditions(
        temperature_c=60.0,
        soc_percent=50.0,
        power_kw=0.0,
        limits=limits,
    )

    assert result.is_valid is False
    assert len(result.issues) == 1

    issue = result.issues[0]

    assert issue.field_name == "temperature_c"
    assert issue.code is ValidationIssueCode.VALUE_OUT_OF_RANGE
    assert issue.severity is IssueSeverity.ERROR
    assert issue.actual_value == 60.0
    assert issue.expected == "temperature_c <= 55.0"


def test_validator_reports_temperature_below_minimum():
    limits = BessOperatingLimits(
        min_temperature_c=-20.0,
        max_temperature_c=55.0,
        min_soc_percent=10.0,
        max_soc_percent=95.0,
        max_charge_power_kw=100.0,
        max_discharge_power_kw=120.0,
    )

    validator = BessEngineeringValidator()

    result = validator.validate_operating_conditions(
        temperature_c=-25.0,
        soc_percent=50.0,
        power_kw=0.0,
        limits=limits,
    )

    assert result.is_valid is False
    assert len(result.issues) == 1

    issue = result.issues[0]

    assert issue.field_name == "temperature_c"
    assert issue.code is ValidationIssueCode.VALUE_OUT_OF_RANGE
    assert issue.severity is IssueSeverity.ERROR
    assert issue.actual_value == -25.0
    assert issue.expected == "temperature_c >= -20.0"


def test_validator_reports_soc_below_minimum():
    limits = BessOperatingLimits(
        min_temperature_c=-20.0,
        max_temperature_c=55.0,
        min_soc_percent=10.0,
        max_soc_percent=95.0,
        max_charge_power_kw=100.0,
        max_discharge_power_kw=120.0,
    )

    validator = BessEngineeringValidator()

    result = validator.validate_operating_conditions(
        temperature_c=25.0,
        soc_percent=5.0,
        power_kw=0.0,
        limits=limits,
    )

    assert result.is_valid is False
    assert len(result.issues) == 1

    issue = result.issues[0]

    assert issue.field_name == "soc_percent"
    assert issue.code is ValidationIssueCode.VALUE_OUT_OF_RANGE
    assert issue.severity is IssueSeverity.ERROR
    assert issue.actual_value == 5.0
    assert issue.expected == "soc_percent >= 10.0"


def test_validator_reports_soc_above_maximum():
    limits = BessOperatingLimits(
        min_temperature_c=-20.0,
        max_temperature_c=55.0,
        min_soc_percent=10.0,
        max_soc_percent=95.0,
        max_charge_power_kw=100.0,
        max_discharge_power_kw=120.0,
    )

    validator = BessEngineeringValidator()

    result = validator.validate_operating_conditions(
        temperature_c=25.0,
        soc_percent=98.0,
        power_kw=0.0,
        limits=limits,
    )

    assert result.is_valid is False
    assert len(result.issues) == 1

    issue = result.issues[0]

    assert issue.field_name == "soc_percent"
    assert issue.code is ValidationIssueCode.VALUE_OUT_OF_RANGE
    assert issue.severity is IssueSeverity.ERROR
    assert issue.actual_value == 98.0
    assert issue.expected == "soc_percent <= 95.0"


def test_validator_reports_discharge_power_above_maximum():
    limits = BessOperatingLimits(
        min_temperature_c=-20.0,
        max_temperature_c=55.0,
        min_soc_percent=10.0,
        max_soc_percent=95.0,
        max_charge_power_kw=100.0,
        max_discharge_power_kw=120.0,
    )

    validator = BessEngineeringValidator()

    result = validator.validate_operating_conditions(
        temperature_c=25.0,
        soc_percent=50.0,
        power_kw=130.0,
        limits=limits,
    )

    assert result.is_valid is False
    assert len(result.issues) == 1

    issue = result.issues[0]

    assert issue.field_name == "power_kw"
    assert issue.code is ValidationIssueCode.VALUE_OUT_OF_RANGE
    assert issue.severity is IssueSeverity.ERROR
    assert issue.actual_value == 130.0
    assert issue.expected == "power_kw <= 120.0"


def test_validator_reports_charge_power_above_maximum():
    limits = BessOperatingLimits(
        min_temperature_c=-20.0,
        max_temperature_c=55.0,
        min_soc_percent=10.0,
        max_soc_percent=95.0,
        max_charge_power_kw=100.0,
        max_discharge_power_kw=120.0,
    )

    validator = BessEngineeringValidator()

    result = validator.validate_operating_conditions(
        temperature_c=25.0,
        soc_percent=50.0,
        power_kw=-110.0,
        limits=limits,
    )

    assert result.is_valid is False
    assert len(result.issues) == 1

    issue = result.issues[0]

    assert issue.field_name == "power_kw"
    assert issue.code is ValidationIssueCode.VALUE_OUT_OF_RANGE
    assert issue.severity is IssueSeverity.ERROR
    assert issue.actual_value == -110.0
    assert issue.expected == "power_kw >= -100.0"


def test_validator_reports_discharge_power_above_soc_dependent_limit():
    limits = BessOperatingLimits(
        min_temperature_c=-20.0,
        max_temperature_c=55.0,
        min_soc_percent=10.0,
        max_soc_percent=95.0,
        max_charge_power_kw=100.0,
        max_discharge_power_kw=120.0,
    )

    soc_discharging_rule = BessSOCDischargingRule(
        full_power_soc_percent=20.0,
        reduced_power_soc_percent=10.0,
        reduced_power_fraction=0.5,
    )

    validator = BessEngineeringValidator()

    result = validator.validate_operating_conditions(
        temperature_c=25.0,
        soc_percent=15.0,
        power_kw=70.0,
        limits=limits,
        soc_discharging_rule=soc_discharging_rule,
    )

    assert result.is_valid is False
    assert len(result.issues) == 1

    issue = result.issues[0]

    assert issue.field_name == "power_kw"
    assert issue.code is ValidationIssueCode.VALUE_OUT_OF_RANGE
    assert issue.severity is IssueSeverity.ERROR
    assert issue.actual_value == 70.0
    assert issue.expected == "power_kw <= 60.0"


def test_validator_allows_discharge_power_at_soc_dependent_limit():
    limits = BessOperatingLimits(
        min_temperature_c=-20.0,
        max_temperature_c=55.0,
        min_soc_percent=10.0,
        max_soc_percent=95.0,
        max_charge_power_kw=100.0,
        max_discharge_power_kw=120.0,
    )

    soc_discharging_rule = BessSOCDischargingRule(
        full_power_soc_percent=20.0,
        reduced_power_soc_percent=10.0,
        reduced_power_fraction=0.5,
    )

    validator = BessEngineeringValidator()

    result = validator.validate_operating_conditions(
        temperature_c=25.0,
        soc_percent=15.0,
        power_kw=60.0,
        limits=limits,
        soc_discharging_rule=soc_discharging_rule,
    )

    assert result.is_valid is True
    assert result.issues == ()


def test_validator_reports_discharge_when_soc_is_below_reduced_threshold():
    limits = BessOperatingLimits(
        min_temperature_c=-20.0,
        max_temperature_c=55.0,
        min_soc_percent=0.0,
        max_soc_percent=95.0,
        max_charge_power_kw=100.0,
        max_discharge_power_kw=120.0,
    )

    soc_discharging_rule = BessSOCDischargingRule(
        full_power_soc_percent=20.0,
        reduced_power_soc_percent=10.0,
        reduced_power_fraction=0.5,
    )

    validator = BessEngineeringValidator()

    result = validator.validate_operating_conditions(
        temperature_c=25.0,
        soc_percent=5.0,
        power_kw=5.0,
        limits=limits,
        soc_discharging_rule=soc_discharging_rule,
    )

    assert result.is_valid is False
    assert len(result.issues) == 1

    issue = result.issues[0]

    assert issue.field_name == "power_kw"
    assert issue.code is ValidationIssueCode.VALUE_OUT_OF_RANGE
    assert issue.severity is IssueSeverity.ERROR
    assert issue.actual_value == 5.0
    assert issue.expected == "power_kw <= 0.0"


def test_validator_allows_full_discharge_power_at_high_soc():
    limits = BessOperatingLimits(
        min_temperature_c=-20.0,
        max_temperature_c=55.0,
        min_soc_percent=0.0,
        max_soc_percent=95.0,
        max_charge_power_kw=100.0,
        max_discharge_power_kw=120.0,
    )

    soc_discharging_rule = BessSOCDischargingRule(
        full_power_soc_percent=20.0,
        reduced_power_soc_percent=10.0,
        reduced_power_fraction=0.5,
    )

    validator = BessEngineeringValidator()

    result = validator.validate_operating_conditions(
        temperature_c=25.0,
        soc_percent=50.0,
        power_kw=120.0,
        limits=limits,
        soc_discharging_rule=soc_discharging_rule,
    )

    assert result.is_valid is True
    assert result.issues == ()