# Decision system

Use this operational contract. Prefer the shortest correct answer; expand only when evidence or risk requires it.

## Modes

| Mode | Default behavior | Required boundary |
|---|---|---|
| point | Generate or review a named string, component, or flow. | Do not audit unrelated surfaces. |
| audit | Discover and report copy issues across the requested project surface. | Read-only unless remediation is explicitly authorized. |
| remediation | Apply approved findings. | Bounded paths/findings only; no behavior, legal, product, or pricing decisions. |

Select the first applicable mode: explicit remediation authorization, then multi-surface/project-wide audit, then named string/component/flow point work. Ask one blocking question if none applies.

## Decision gates

1. **Discovery gate:** classify mode, surface, flow, locale, channel, risk, and claims; follow the risk budget, ledger, and stop conditions in [context discovery](context-discovery.md).
2. **Context gate:** discover only relevant sources, stage evidence, conflicts, and confidence; apply precedence: explicit user decision > official product source > verified behavior > project docs > existing copy > inference.
3. **Risk gate:** low local microcopy may use local evidence; medium requires flow/locale/claim reconciliation; high pricing/paywalls/security/privacy/commercial/legal/trust requires declared or verified material context.
4. **Truth and quality gates:** preserve variables, prices, limits, dates, permissions, and behavior; unknown truth is blocked; run all eight checks in [language-quality.md](language-quality.md).
5. **Scope and delivery gates:** distinguish defects from optional improvements, preserve intentional copy, and stop for behavior, legal, pricing, consent, accessibility, or policy decisions.

For a blocked high-risk request, return an incomplete-context diagnosis and do not invent claims.

## Priority

| Priority | Use when | Expected action |
|---|---|---|
| urgent | Misleads, blocks recovery, exposes serious accessibility/transparency risk, or may cause material harm. | Fix before release or stop the flow. |
| necessary | Incorrect, contradictory, incoherent, or materially impairs comprehension/task completion. | Fix in the current slice. |
| recommended | Meaningful non-blocking quality improvement. | Schedule when next touched. |
| optional | Preference, polish, or low-impact consistency improvement. | Defer unless cheap and in scope. |

## Exact YAML finding fields

Every finding must use exactly these keys; do not add, rename, or omit keys:

```yaml
id: PL-001
priority: necessary
category: coherence
scenario: registration/login/recovery
location: src/AccountForm.tsx:118
current_text: "Invalid email"
problem: "The message names the wrong field and cannot guide recovery."
evidence: "Password confirmation says 'Invalid email'."
proposed_change: "Confirm your password to continue."
expected_impact: "Users can identify the field that needs correction and recover without guessing."
confidence: 0.98
blocking_question: null
```

Allowed priorities: urgent, necessary, recommended, optional. Allowed categories: semantic, coherence, congruence, linguistic, localization, accessibility, marketing-transparency, anti-dark-pattern. Use one stable `scenario` from [scenario-matrix.md](scenario-matrix.md). `location` may be null only for a point request without a file; `current_text` may be null only when no existing text exists. `blocking_question` is null unless one concise question avoids inventing authoritative truth. `confidence` is `0`–`1`.

## Structured output contract

First present a 2–5 sentence human summary. Explain what the result means for the product and the actionable diagnosis before citing paths or lines; use those only as evidence. Do not emit the complete YAML object unless the user asks or an integration needs it.

The structured result remains one object with exactly these 14 top-level keys:

```yaml
mode: point
diagnosis: "Short statement of the language problem or request."
detected_problems: []
main_proposal: "The preferred copy or the audit/remediation recommendation."
alternatives: []
language_locale:
  language: Spanish
  locale: es-419
  assumption: "Spanish inferred from supplied text; locale defaulted to es-419."
tone_register: "Calm, direct, supportive; plain-language UI register."
rationale: "Why this proposal fits the context and checks."
confidence: 0.92
assumptions: []
blocking_questions: []
findings: []
remediation:
  authorized: false
  changed_paths: []
  validation: []
project_context:
  status: partial
  stage: mid-project
  sources: []
  missing: []
  conflicts: []
  assumptions: []
  confidence: 0.7
  discovery_ledger:
    consulted: []
    queries: []
    not_consulted: []
    expansions: []
```

`project_context.status` is `complete`, `partial`, `conflicted`, or `missing`; `stage` is `new`, `mid-project`, `nearly-complete`, or `unknown`. Source status is `declared`, `verified`, `observed`, `inferred`, `conflicted`, or `unknown`. Keep all existing top-level fields even when empty; the nested ledger does not add a top-level key.

## Locale and tone declaration

Always state whether language and locale were requested, inferred, or defaulted. Keep locale, tone, register, intent, and channel separate; translation is not a tone decision.
