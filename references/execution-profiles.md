# Execution profiles

Execution profiles control investigation depth and cost. They are independent of operation mode and the `compose` route. Choose one profile first, then apply `point`, `audit`, or `remediation` boundaries. If unspecified, auto-select `balanced` and report it in `project_context`.

## Routing and budgets

| Profile | Auto-selection and evidence budget | Agent/verifier policy |
|---|---|---|
| `light` | One named low-risk surface; 1–2 files, 1 focused query, 1 fragment. | No broad inventory or subagent by default. Escalate only for risk, contradiction, or explicit request. |
| `balanced` | Default; up to 5 candidate files, 3 targeted queries, 3 fragments. | One bounded sequential agent only when broader exploration or multi-file writing is justified. |
| `performance` | Explicit depth/validation, related-flow comparison, or high-risk evidence; up to 8 relevant files, 5 queries, 5 fragments. | Independent verifier only for high risk, authoritative conflict, or requested validation. |

Budgets are initial reads, not quotas to exhaust. Stop as soon as risk-appropriate evidence is sufficient. A high-risk gate still blocks unsupported claims in every profile. “Performance” means depth and quality, not speed.

## Reuse and invalidation

Reuse a context fragment within a session or a resumable run only when its source content hash, normalized query, scope, locale, risk, and precedence inputs match. Store the hash and cache decision in the discovery ledger. Invalidate and record the reason when a source changes, the scope/locale/risk changes, user instructions change, the authoritative source changes, or a fresh audit is requested. Never reuse a stale/conflicted high-risk fragment as verified evidence.

For benchmark or repeated runs, keep a content-hash ledger with: `source_hash`, `query_hash`, `profile`, `scope`, `cache_status`, `invalidated_reason`, and timestamp when available. A cache hit can reduce reads, but it cannot change the output contract or suppress a required high-risk check.

## Reporting

Normal compose returns visible copy only and never exposes profile, diagnosis, rationale, findings, project context, or telemetry. Formal audit, remediation, localization/context, or explicitly requested reports keep the exact 14 top-level output keys and 12-key finding schema. Put the selected profile at `project_context.execution_profile` or in the nested discovery ledger; never create a new top-level key. Report missing telemetry as unknown/null, never as zero or an estimate.

## Examples

- `modo ligero: mejora este CTA`: inspect the CTA and immediate context only.
- `modo balanceado: auditá este onboarding`: use progressive discovery and a bounded sequential agent only if justified.
- `modo rendimiento: validá pricing y registro`: compare only those related flows and use a verifier only when a high-risk or conflict gate warrants it.
