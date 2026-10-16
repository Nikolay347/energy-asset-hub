import sqlite3
import json

from energy_asset_hub.domain.models.bess_engineering_validation_outcome import (
    BessEngineeringValidationOutcome,
)
from energy_asset_hub.domain.models.bess_operating_limits import (
    BessOperatingLimits,
)
from energy_asset_hub.domain.models.bess_soc_discharging_rule import (
    BessSOCDischargingRule,
)
from energy_asset_hub.domain.models.resolved_bess_limits import (
    BessLimitsResolutionReason,
    BessLimitsSource,
    ResolvedBessLimits,
)
from energy_asset_hub.domain.models.resolved_bess_soc_discharging_rule import (
    BessSOCDischargingRuleResolutionReason,
    BessSOCDischargingRuleSource,
    ResolvedBessSOCDischargingRule,
)
from energy_asset_hub.domain.validation.validation_result import (
    ValidationResult,
)
from energy_asset_hub.domain.validation.enums import (
    IssueSeverity,
    ValidationIssueCode,
)
from energy_asset_hub.domain.validation.validation_issue import (
    ValidationIssue,
)


class SQLiteBessEngineeringValidationOutcomeRepository:
    def __init__(self, connection: sqlite3.Connection):
        self._connection = connection
        self._create_table()

    def _create_table(self) -> None:
        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS bess_engineering_validation_outcomes (
                packet_id TEXT NOT NULL,
                attempt_number INTEGER NOT NULL,

                min_temperature_c REAL NOT NULL,
                max_temperature_c REAL NOT NULL,
                min_soc_percent REAL NOT NULL,
                max_soc_percent REAL NOT NULL,
                max_charge_power_kw REAL NOT NULL,
                max_discharge_power_kw REAL NOT NULL,

                limits_source TEXT NOT NULL,
                limits_reason TEXT NOT NULL,

                full_power_soc_percent REAL NOT NULL,
                reduced_power_soc_percent REAL NOT NULL,
                reduced_power_fraction REAL NOT NULL,

                soc_rule_source TEXT NOT NULL,
                soc_rule_reason TEXT NOT NULL,

                PRIMARY KEY (packet_id, attempt_number),
                
                FOREIGN KEY (packet_id, attempt_number)
                    REFERENCES processing_attempts(
                        packet_id,
                        attempt_number
                    )
            )
            """
        )

        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS bess_engineering_validation_issues (
                issue_id INTEGER PRIMARY KEY AUTOINCREMENT,
                packet_id TEXT NOT NULL,
                attempt_number INTEGER NOT NULL,
                field_name TEXT,
                code TEXT NOT NULL,
                severity TEXT NOT NULL,
                message TEXT NOT NULL,
                actual_value TEXT,
                expected TEXT,

                FOREIGN KEY (packet_id, attempt_number)
                    REFERENCES bess_engineering_validation_outcomes(
                        packet_id,
                        attempt_number
                    )
            )
            """
        )

        self._connection.commit()

    def save(
        self,
        packet_id: str,
        attempt_number: int,
        outcome: BessEngineeringValidationOutcome,
    ) -> None:
        limits = outcome.resolved_limits.limits
        soc_rule = outcome.resolved_soc_rule.rule

        self._connection.execute(
            """
            INSERT INTO bess_engineering_validation_outcomes (
                packet_id,
                attempt_number,
                min_temperature_c,
                max_temperature_c,
                min_soc_percent,
                max_soc_percent,
                max_charge_power_kw,
                max_discharge_power_kw,
                limits_source,
                limits_reason,
                full_power_soc_percent,
                reduced_power_soc_percent,
                reduced_power_fraction,
                soc_rule_source,
                soc_rule_reason
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                packet_id,
                attempt_number,
                limits.min_temperature_c,
                limits.max_temperature_c,
                limits.min_soc_percent,
                limits.max_soc_percent,
                limits.max_charge_power_kw,
                limits.max_discharge_power_kw,
                outcome.resolved_limits.source.value,
                outcome.resolved_limits.reason.value,
                soc_rule.full_power_soc_percent,
                soc_rule.reduced_power_soc_percent,
                soc_rule.reduced_power_fraction,
                outcome.resolved_soc_rule.source.value,
                outcome.resolved_soc_rule.reason.value,
            ),
        )

        for issue in outcome.validation_result.issues:
            self._connection.execute(
                """
                INSERT INTO bess_engineering_validation_issues (
                    packet_id,
                    attempt_number,
                    field_name,
                    code,
                    severity,
                    message,
                    actual_value,
                    expected
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    packet_id,
                    attempt_number,
                    issue.field_name,
                    issue.code.name,
                    issue.severity.value,
                    issue.message,
                    json.dumps(issue.actual_value),
                    json.dumps(issue.expected),
                ),
            )

        self._connection.commit()

    def get(
        self,
        packet_id: str,
        attempt_number: int,
    ) -> BessEngineeringValidationOutcome | None:
        cursor = self._connection.execute(
            """
            SELECT
                min_temperature_c,
                max_temperature_c,
                min_soc_percent,
                max_soc_percent,
                max_charge_power_kw,
                max_discharge_power_kw,
                limits_source,
                limits_reason,
                full_power_soc_percent,
                reduced_power_soc_percent,
                reduced_power_fraction,
                soc_rule_source,
                soc_rule_reason
            FROM bess_engineering_validation_outcomes
            WHERE packet_id = ?
              AND attempt_number = ?
            """,
            (
                packet_id,
                attempt_number,
            ),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        issues_cursor = self._connection.execute(
            """
            SELECT
                field_name,
                code,
                severity,
                message,
                actual_value,
                expected
            FROM bess_engineering_validation_issues
            WHERE packet_id = ?
              AND attempt_number = ?
            ORDER BY issue_id
            """,
            (
                packet_id,
                attempt_number,
            ),
        )

        issue_rows = issues_cursor.fetchall()

        issues = tuple(
            ValidationIssue(
                field_name=issue_row[0],
                code=ValidationIssueCode[issue_row[1]],
                severity=IssueSeverity(issue_row[2]),
                message=issue_row[3],
                actual_value=json.loads(issue_row[4]),
                expected=json.loads(issue_row[5]),
            )
            for issue_row in issue_rows
        )

        limits = BessOperatingLimits(
            min_temperature_c=row[0],
            max_temperature_c=row[1],
            min_soc_percent=row[2],
            max_soc_percent=row[3],
            max_charge_power_kw=row[4],
            max_discharge_power_kw=row[5],
        )

        resolved_limits = ResolvedBessLimits(
            limits=limits,
            source=BessLimitsSource(row[6]),
            reason=BessLimitsResolutionReason(row[7]),
        )

        soc_rule = BessSOCDischargingRule(
            full_power_soc_percent=row[8],
            reduced_power_soc_percent=row[9],
            reduced_power_fraction=row[10],
        )

        resolved_soc_rule = ResolvedBessSOCDischargingRule(
            rule=soc_rule,
            source=BessSOCDischargingRuleSource(row[11]),
            reason=BessSOCDischargingRuleResolutionReason(row[12]),
        )

        return BessEngineeringValidationOutcome(
            validation_result=ValidationResult(
                issues=issues,
            ),
            resolved_limits=resolved_limits,
            resolved_soc_rule=resolved_soc_rule,
        )