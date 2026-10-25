# Adaptive Product Language

Adaptive Product Language generates, reviews, audits, and explicitly remediates user-facing copy as product behavior. It investigates only enough context for the risk, then explains the product impact in plain language before returning structured data.

## Quick path

1. Start with the named surface or flow; do not ask the skill to read the whole repository by default.
2. It inventories candidates, searches targeted hypotheses, and reads only relevant fragments.
3. It stops when evidence is sufficient, or blocks high-risk claims without authoritative evidence.
4. Audit/remediation output includes a compact discovery ledger; the response starts with a human summary, not a YAML dump.

## Installation

### Project-local

```bash
mkdir -p .agents/skills
git clone https://github.com/RicardoGurrola15/adaptive-product-language.git .agents/skills/adaptive-product-language
```

### Global

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/RicardoGurrola15/adaptive-product-language.git ~/.codex/skills/adaptive-product-language
```

The package has no private API, framework, runtime, external tool, or model-provider dependency.

## Distribution

Official repository: <https://github.com/RicardoGurrola15/adaptive-product-language>

To install from GitHub, clone or download this repository and copy its root directory into your local skills directory (for example, `~/.codex/skills/adaptive-product-language`). For a local checkout, copy this package directory into the same destination. Invoke it explicitly as `adaptive-product-language`.

This package requires no private APIs or dependencies.

## Portability

This is a portable, platform-neutral Agent Skills package usable by Codex, Claude, Gemini CLI, and other agents or hosts that support the Agent Skills convention or can load Markdown instructions. The package core is `SKILL.md` plus its references, assets, and evals; `agents/openai.yaml` is optional Codex/OpenAI metadata. Installation and discovery are host-specific, and GitHub provides distribution rather than a universal installer. There are no private APIs, MCP, proprietary tools, runtime dependencies, or model dependencies. If a host has no automatic discovery, load the package manually and explicitly invoke `adaptive-product-language`.

## Efficient investigation

| Request | Initial budget | Escalate only when |
|---|---|---|
| Point / low risk | 1–3 files, 1 targeted search | A contradiction, material claim, real dependency, or explicit request appears. |
| Medium risk | Up to 5 candidates, 3 queries, 3 fragments | Flow, locale/glossary, or claim evidence needs reconciliation. |
| High risk / audit | Inventory first, up to 5 initial queries | A material claim needs declared or verified evidence. |

An explicit request for all documentation is honored and recorded as an expansion. By default, 1–3 files use no subagent; broader exploration uses one sequential bounded explorer, multi-file writing one writer, and a second verifier only for high risk, authoritative conflict, or requested validation.

## Context initialization and audit

```text
Bootstrap product-language context for this new project. Use the template as a proposal only; do not create .product-language/context.yaml. Record declared facts, unknowns, sources, and confidence.
```

```text
Reconcile product-language context for this checkout flow. Use progressive discovery, report consulted evidence and grouped exclusions, and do not edit files.
```

```text
Run a read-only context drift audit for the pricing journey. Compare only relevant copy with context, verified behavior, pricing/policy sources, and locales; return a blocked diagnosis if a material claim lacks evidence.
```

## Invocation examples

### Point generation

> Generate a primary CTA and secondary action for a listing form. Infer the Spanish locale, declare the assumption, and use only verified local behavior.

### High-risk review

> Review this paywall. If declared or verified pricing, cadence, eligibility, and renewal context is absent, return an incomplete-context diagnosis instead of rewriting claims.

### Bounded remediation

> Apply only necessary copy fixes from findings PL-004 and PL-009. Do not change behavior, pricing, legal meaning, or unrelated files. Report changed paths and validation.

## Validation

Check frontmatter, required markers, local links, and YAML under `agents/` and `evals/`. Confirm the exact 14-key output contract, unchanged 12-key finding schema, progressive budgets, ledger, stop conditions, sequential-agent policy, source precedence, and Context Gate cases in [context-fixtures.yaml](evals/context-fixtures.yaml).

## Limitations

The skill cannot infer authoritative product policy, legal requirements, pricing truth, runtime behavior, or accessibility conformance from copy alone. It must stop and escalate rather than guess.
