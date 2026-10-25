# Audit and remediation

## Read-only discovery

Default to audit mode and do not edit. Establish project stage, classify flow/risk/claims, and follow the progressive protocol in [context discovery](context-discovery.md). Inventory candidate paths without opening them fully, search related terms together, inspect the smallest relevant fragments, and record the ledger before interpreting gaps.

Do not search every UI component, route, locale, document, or system state by default. Start with the requested surface and expand only for contradiction, a material claim, a real dependency, or an explicit request. For each finding, group by flow, quote the smallest useful excerpt, record visibility/trigger, and never infer runtime behavior from a label alone.

## Agent policy

| Scope | Default execution |
|---|---|
| 1–3 files | No subagent. |
| 4+ exploratory files | One sequential, bounded explorer. |
| 2+ writing files | One writer. |
| High risk, authoritative contradiction, or requested validation | One additional verifier only. |

Never run parallel explorers for the same audit. The next agent receives only a compact handoff: routes, lines/sections, evidence state, ledger, and unanswered questions. It must not restart discovery. Run tests/builds only when requested or required by the change, and delegate that execution once.

## Context handling

- Discover the canonical context record and supported fallbacks only when relevant to the flow or claim; reuse adequate glossaries, brand guides, and locale resources.
- For medium-risk copy, reconcile available sources and declare assumptions.
- For high-risk pricing, paywall, security, privacy, commercial, legal, or trust copy, require declared or verified context. Otherwise produce an incomplete-context diagnosis, preserve the surface, and ask one blocking question.
- For nearly-complete projects, run the read-only [context drift audit](context-drift-audit.md) before polish only for the relevant release surface.

## Remediation authorization

Remediation requires an explicitly named bounded target: finding IDs, files, flow, or clear change set. Before editing, confirm target and exclusions; preserve variables, keys, markup, links, and behavior; make the smallest copy-only change; re-check neighboring states and supported locales; and report changed paths, unresolved questions, and validation.

## Stop and escalate

Stop instead of editing for behavior-dependent blockers; contradictory authoritative price, limits, entitlements, or renewal data; legal, consent, safety, privacy, or policy decisions; unsupported claims; or unclear source-of-truth conflicts. Put the concise question in both the finding's unchanged `blocking_question` field and top-level `blocking_questions`; do not hide uncertainty in a confident rewrite.
