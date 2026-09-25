from energy_asset_hub.integrations.bess_api.payload_validator import (
    BessTelemetryPayloadValidator,
)
from energy_asset_hub.domain.validation.enums import (
    IssueSeverity,
    ValidationIssueCode,
)


def test_valid_payload_has_no_issues():
    validator = BessTelemetryPayloadValidator()
    data = {
        "asset_id": "BESS-01",
        "timestamp": "2026-09-25T08:00:00Z",
        "soc_percent": 72.5,
        "power_kw": -120.0,
        "temperature_c": 28.4,
    }
    result = validator.validate(data)

    assert result.is_valid is True
    assert result.issues == ()


def test_missing_temperature_field_returns_issue():
    validator = BessTelemetryPayloadValidator()

    data = {
        "asset_id": "BESS-01",
        "timestamp": "2026-09-25T08:00:00Z",
        "soc_percent": 72.5,
        "power_kw": -120.0,
    }

    result = validator.validate(data)

    assert result.is_valid is False
    assert len(result.issues) == 1


    issue = result.issues[0]

    assert issue.field_name == "temperature_c"
    assert issue.code is ValidationIssueCode.MISSING_FIELD
    assert issue.severity is IssueSeverity.ERROR


def test_invalid_soc_type_returns_issue():
    validator = BessTelemetryPayloadValidator()

    data = {
        "asset_id": "BESS-01",
        "timestamp": "2026-09-25T08:00:00Z",
        "soc_percent": "72.5",
        "power_kw": -120.0,
        "temperature_c": 28.4,
    }

    result = validator.validate(data)

    assert result.is_valid is False
    assert len(result.issues) == 1

    issue = result.issues[0]

    assert issue.field_name == "soc_percent"
    assert issue.code is ValidationIssueCode.INVALID_TYPE
    assert issue.severity is IssueSeverity.ERROR


def test_bool_soc_value_returns_invalid_type_issue():
    validator = BessTelemetryPayloadValidator()

    data = {
        "asset_id": "BESS-01",
        "timestamp": "2026-09-25T08:00:00Z",
        "soc_percent": True,
        "power_kw": -120.0,
        "temperature_c": 28.4,
    }

    result = validator.validate(data)

    assert result.is_valid is False
    assert len(result.issues) == 1

    issue = result.issues[0]

    assert issue.field_name == "soc_percent"
    assert issue.code is ValidationIssueCode.INVALID_TYPE
    assert issue.severity is IssueSeverity.ERROR


def test_multiple_validation_issues_are_collected():
    validator = BessTelemetryPayloadValidator()

    data = {
        "asset_id": "BESS-01",
        "soc_percent": "72.5",
        "power_kw": -120.0,
        "temperature_c": 28.4,
    }

    result = validator.validate(data)

    assert result.is_valid is False
    assert len(result.issues) == 2

    issues_by_field = {
        issue.field_name: issue
        for issue in result.issues
    }

    timestamp_issue = issues_by_field["timestamp"]

    assert timestamp_issue.code is ValidationIssueCode.MISSING_FIELD
    assert timestamp_issue.severity is IssueSeverity.ERROR

    soc_issue = issues_by_field["soc_percent"]

    assert soc_issue.code is ValidationIssueCode.INVALID_TYPE
    assert soc_issue.severity is IssueSeverity.ERROR

