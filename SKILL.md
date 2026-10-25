---
name: adaptive-product-language
description: "Trigger: product language, UX copy, localization, copy audit, bilingual UI, CTA, pricing, onboarding, errors. Generate, review, or audit contextual product copy."
license: Apache-2.0
metadata:
  author: "casamapa"
  version: "0.4.0"
---

## Activation Contract

Use for copy requests, read-only audits, or explicitly authorized bounded remediation. Treat UI language as product behavior. **Texto sin contexto es ser errático.**

## Portability

This is a portable, platform-neutral Agent Skills package: the core is `SKILL.md` plus its references, assets, and evals. `agents/openai.yaml` is optional Codex/OpenAI metadata; installation and discovery are host-specific. GitHub is a distribution channel, not a universal installer. The package has no private APIs, MCP, proprietary tools, runtime dependencies, or model dependencies. Hosts without automatic discovery can load the package manually and explicitly invoke `adaptive-product-language`.

## Hard Rules

- Investigate progressively: classify first, inventory paths, search hypotheses, read relevant fragments, then stop when evidence meets risk.
- Do not read a repository, documentation tree, or reference cascade by default. Expand only for contradiction, material claim, real dependency, or explicit request; record the reason.
- Preserve behavior, prices, limits, legal meaning, consent, variables, and intentional correct copy. Never invent product facts.
- Audit is read-only; remediation needs explicit bounded authorization. Use one sequential, bounded agent only when the work exceeds local inspection.


## Execution profiles

Select an execution profile separately from the operation mode (`point`, `audit`, or `remediation`). If the user does not specify one, use **balanced** and declare `execution_profile: balanced` inside `project_context` (or its `discovery_ledger`). Users may say “modo ligero”, “modo balanceado”, or “modo rendimiento”. “Performance” means greater depth and quality, **not faster execution**; never silently upgrade the selected profile. High-risk gates apply in every profile.

| Profile | Use | Budget and agent boundary |
|---|---|---|
| `light` | Simple microcopy or a tightly named surface. | Lowest cost: local evidence, 1–2 files, one focused search, no broad inventory or subagent by default. Escalate only for risk, contradiction, or an explicit request. |
| `balanced` (default) | Normal point work, audits, and bounded remediation. | Current progressive budgets: classify, inventory candidates, targeted searches, relevant fragments, then stop at sufficient evidence. Use one bounded sequential agent only when justified by broader exploration or multi-file writing. |
| `performance` | High-value review, cross-flow consistency, or requested depth. | Highest depth and cost: inspect broader relevant evidence and compare related flows/locales. Use an independent verifier only for high-risk work, authoritative conflict, or requested validation; never read unbounded or automatically scan the repository. |

Compact examples: “modo ligero: mejora este CTA” stays local; “modo balanceado: auditá este onboarding” uses progressive evidence; “modo rendimiento: validá consistencia entre pricing y registro” expands only across those related flows. Record the chosen profile in `project_context`, without adding a top-level output key. See [execution profiles](references/execution-profiles.md) for routing details.

## Decision Gates

| Situation | Action |
|---|---|
| Low-risk local microcopy | Consult local context and restrictions; state uncertainty. |
| Medium onboarding, landing, product, or SEO | Search the flow, locale/glossary, and highest claim source. |
| High pricing, paywall, security, privacy, commercial, legal, or trust copy | Require declared or verified evidence per material claim; block if absent. |
| New, existing, or nearly-complete project | Bootstrap, reconcile, or drift-audit only the relevant sources. |

## Execution Steps

1. Select mode (remediation, audit, point), then classify surface, flow, locale, channel, risk, and claims.
2. Follow the progressive discovery budgets and `project_context.discovery_ledger` in [context discovery](references/context-discovery.md).
3. Apply source precedence, risk gates, quality checks, and scenario matrix; stop at sufficient evidence and rank findings.
4. For authorized remediation, change only named findings and verify only the affected scope.

## Output Contract

Start with a 2–5 sentence human summary: product meaning first, actionable diagnosis second, paths/lines only as supporting evidence. Then return the exact 14-key object in [decision-system.md](references/decision-system.md); do not dump full YAML unless requested or needed for integration. Preserve the exact 12-key finding schema. `project_context` may contain the compact discovery ledger.

## References

- [Decision system](references/decision-system.md)
- [Project context](references/project-context.md)
- [Context discovery](references/context-discovery.md)
- [Context drift audit](references/context-drift-audit.md)
- [Audit and remediation](references/audit-and-remediation.md)
- [Language quality](references/language-quality.md)
- [Scenario matrix](references/scenario-matrix.md)
- [Tone and register](references/tone-and-register.md)
- [Localization](references/localization-guide.md)
- [Component rules](references/component-rules.md)
- [Terminology](references/terminology.md)
- [Anti-patterns](references/anti-patterns.md)
- [Examples](references/examples.md)
