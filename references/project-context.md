# Project context

## Principle

**Texto sin contexto es ser errático.** Context is the evidence used to decide whether copy is safe to generate, audit, or remediate.

## Context record

Use the reusable [template](../assets/context-template.yaml); do not require it to exist in a project.

| Field | Meaning |
|---|---|
| status | `complete`, `partial`, `conflicted`, or `missing`. |
| stage | `new`, `mid-project`, `nearly-complete`, or `unknown`. |
| sources | Consulted paths with evidence status and confidence. |
| missing | Facts needed for safe output. |
| conflicts | Contradictory facts, their sources, and escalation. |
| assumptions | Explicit non-authoritative working assumptions. |
| confidence | Overall confidence from `0` to `1`. |
| discovery_ledger | Compact audit trail of consulted evidence, searches, grouped exclusions, and justified expansions. |

`discovery_ledger` is required in audit/remediation and optional/compact for point work. Its `consulted` entries include target, range/section, method, and purpose; `queries` include query, scope, and result summary; `not_consulted` groups exclusions with reasons; and `expansions` gives the reason for each read, query, or agent beyond the initial budget.

## Evidence states and precedence

Use `declared` for an explicit user/product decision, `verified` for behavior proven by code or tests, `observed` for directly read content, `inferred` for reasoned but unconfirmed context, `conflicted` for incompatible evidence, and `unknown` when no usable evidence exists. Always include confidence.

Resolve facts in this order: **explicit user decision > official product source > verified behavior > project docs > existing copy > inference**. Existing copy can reveal terminology or intent, but never establishes product truth.

## Context gate and sufficiency

| Risk | Minimum context | Stop condition |
|---|---|---|
| low | Local context and restrictions | No facts are introduced. |
| medium | Flow fragments, locale/glossary, and highest-precedence claim source | Targeted searches find no contradiction. |
| high | `declared` or `verified` evidence for every material claim | Otherwise diagnose incomplete context and block the claim. |

Expansion requires a recorded contradiction, material claim, real dependency, or explicit user request. For a high-risk gap, return `project_context.status: missing` or `partial`, the missing facts, and a blocking question. Do not invent claims.
