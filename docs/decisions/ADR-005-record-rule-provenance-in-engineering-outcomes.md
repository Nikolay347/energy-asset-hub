# ADR-005 — Record rule provenance in engineering-validation outcomes

- **Status:** Accepted
- **Date:** 2026-10-

## Context

An engineering-validation result is not fully auditable if it records only pass/fail diagnostics. The system must also be able to explain which limits and rules were actually applied and why they were selected.

## Decision

Engineering validation operates on resolved rule objects that include both the effective rule and its provenance.

Current provenance contains:

- `source` — for example `DEFAULT` or `EXTERNAL`;
- `reason` — for example external rule found, not found, or repository unavailable.

`BessEngineeringValidationOutcome` stores the resolved limits and resolved SOC discharge rule together with validation diagnostics. SQLite persistence stores the effective rule values plus their source and reason.

## Consequences

- Historical outcomes can explain why a particular rule was used.
- Fallback behavior is visible instead of hidden.
- Auditing and future reporting are easier.
- Rule/version identifiers are a natural future extension but are not yet part of the current persisted model.

## Related components

- `ResolvedBessLimits`
- `ResolvedBessSOCDischargingRule`
- `BessEngineeringValidationOutcome`
- `SQLiteBessEngineeringValidationOutcomeRepository`
