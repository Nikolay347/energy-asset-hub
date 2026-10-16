# Architecture Decision Records

Architecture Decision Records (ADRs) capture important design decisions and the reasons behind them.

| ADR                                                                                    | Decision                                                         | Status   |
|----------------------------------------------------------------------------------------|------------------------------------------------------------------|----------|
| [ADR-001](ADR-001-persist-raw-packet-before-processing.md)                             | Persist raw telemetry packet before processing                   | Accepted |
| [ADR-002](ADR-002-separate-structural-and-engineering-validation.md)                   | Separate structural validation from engineering validation       | Accepted |
| [ADR-003](ADR-003-use-repository-contracts-for-persistence-boundaries.md)              | Use repository contracts at persistence boundaries               | Accepted |
| [ADR-004](ADR-004-use-default-fallback-rules-when-external-rules-are-unavailable.md)   | Use configured default rules as fallback                         | Accepted |
| [ADR-005](ADR-005-record-rule-provenance-in-engineering-outcomes.md)                   | Record rule provenance in engineering outcomes                   | Accepted |
| [ADR-006](ADR-006-number-processing-attempts-per-packet.md)                            | Number processing attempts independently per packet              | Accepted |
| [ADR-007](ADR-007-preserve-measurements-when-engineering-validation-reports-issues.md) | Preserve measurements when engineering validation reports issues | Accepted |
| [ADR-008](ADR-008-use-application-service-as-pipeline-orchestrator.md)                 | Use an application service as the packet-processing orchestrator | Accepted |

## ADR lifecycle

- **Proposed** — under discussion.
- **Accepted** — current architectural decision.
- **Superseded** — replaced by a later ADR; keep the old record for history.
- **Deprecated** — no longer recommended, but not necessarily replaced by one specific ADR.

Do not renumber existing ADRs. If a decision is replaced, create a new ADR and link the old and new records.
