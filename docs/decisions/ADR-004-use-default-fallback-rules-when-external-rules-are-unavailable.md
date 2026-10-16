# ADR-004 — Use configured default rules as fallback when external rules are unavailable

- **Status:** Accepted
- **Date:** 2026-10-

## Context

Engineering validation requires operating limits and SOC discharge rules. External repositories may return no asset-specific rule or may be temporarily unavailable.

Stopping all validation in those cases would make the system unnecessarily fragile.

## Decision

For configured BESS assets, resolve rules using the following strategy:

1. Try the external repository.
2. If an external rule exists, use it.
3. If it is not found, use the configured default rule.
4. If the external repository is unavailable, use the configured default rule.
5. If the asset itself is not configured, raise an explicit error instead of silently inventing configuration.

The same principle is used for operating limits and SOC discharge rules.

## Consequences

- Engineering validation can continue during external repository outages.
- Missing asset-specific data does not automatically disable validation.
- Every configured asset must have an applicable default configuration.
- Unknown assets fail explicitly rather than receiving an accidental global rule.

## Related components

- `ConfiguredBessRegistry`
- `DefaultBessLimitsRegistry`
- `DefaultBessSOCDischargingRuleRegistry`
- `BessLimitsResolver`
- `BessSOCDischargingRuleResolver`
