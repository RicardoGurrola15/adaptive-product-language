# Execution profiles

Execution profiles control investigation depth and cost. They are independent of operation mode: choose one profile, then apply `point`, `audit`, or `remediation` boundaries. If unspecified, choose `balanced` and report `execution_profile: balanced` inside `project_context` or `project_context.discovery_ledger`.

## Routing

| Profile | Evidence budget | Agent/verifier policy |
|---|---|---|
| `light` | Named surface, local context, 1–2 files, one focused search. | No broad inventory or subagent by default. Escalate only for a high-risk gate, contradiction, or explicit request. |
| `balanced` | Progressive discovery: classify, inventory candidates, targeted queries, relevant fragments, and stop at risk-appropriate sufficiency. | One bounded sequential agent when broader exploration or multi-file writing is justified. |
| `performance` | Broader **relevant** sources, related flows, and locale/claim consistency checks. | Independent verifier only for high-risk work, authoritative conflict, or requested validation. Never unbounded reading or automatic repository-wide work. |

“Performance” means more depth and quality, not faster execution. Do not silently upgrade a selected profile. Recognize `modo ligero`, `modo balanceado`, and `modo rendimiento`. High-risk evidence and blocking rules remain unchanged in every profile.

## Examples

- `modo ligero: mejora este CTA`: inspect the CTA and its immediate component context; do not inventory the app.
- `modo balanceado: auditá este onboarding`: use the normal progressive budgets and a bounded sequential agent only if the flow spans enough files to justify it.
- `modo rendimiento: validá pricing y registro`: compare only those related flows/locales, and add an independent verifier only when high-risk, conflicting authority, or validation was requested.

## Reporting

Keep the existing 14 top-level output keys and 12-key finding schema. Put the selected profile at `project_context.execution_profile` or in the nested discovery ledger; never create a new top-level key.
