# Decision system

Use this operational contract. Prefer the shortest correct answer; expand only when evidence or risk requires it.

## Routes and modes

The `compose` route coordinates copy for a new or existing screen, component, form, flow, or marketing section. It is a routing instruction, not a fifth output mode: report `mode: point` for a named new surface, `mode: audit` for an existing multi-surface review, and `mode: remediation` only after explicit bounded authorization.

| Mode | Default behavior | Required boundary |
|---|---|---|
| point | Generate or review a named string, component, screen, or flow. | Do not audit unrelated surfaces. |
| audit | Discover and report copy issues across the requested project surface. | Read-only unless remediation is explicitly authorized. |
| remediation | Apply approved findings. | Bounded paths/findings only; no behavior, legal, product, or pricing decisions. |

Select the first applicable route/mode: explicit remediation authorization, then an existing multi-surface audit, then a named string/surface point request. Use `compose` inside the selected mode when coordinated copy is requested. Ask one blocking question if no mode or authoritative requirement can be inferred.

## Output tiers

Use **copy-only** output for normal compose work: return only the requested visible copy, organized by the named surface sections. Do not emit a summary, diagnosis, rationale, assumptions, findings, project context, profile, or telemetry. Use **compact** output for normal non-compose point work. Use **formal** output for audit, remediation, localization/context reports, or an explicit formal request: begin with a 2–5 sentence human summary, then emit exactly the 14-key object below and preserve the exact 12-key finding schema. Human summaries and prose values MUST use the requested or inferred locale; fixed schema keys and route identifiers may remain English. In particular, `es-419` must never receive an English human summary. The tier changes presentation only; it never relaxes evidence, authorization, or risk gates.

## Automatic profile selection

Profile selection is separate from mode. Honor an explicit profile or `modo ligero`, `modo balanceado`, or `modo rendimiento`. Otherwise select `performance` only when the user requests depth/validation, the work spans related flows, or the risk gate is high; select `light` for one named low-risk local surface; select `balanced` for all other requests. Once selected, do not silently upgrade or downgrade. Declare `project_context.execution_profile`.

## Decision gates

1. **Discovery gate:** classify mode/route, surface, flow, locale, channel, audience, behavior, risk, and material claims; follow the profile budget, cache, ledger, and stop conditions in [context discovery](context-discovery.md).
2. **Context gate:** discover only relevant sources, stage evidence, conflicts, and confidence; apply precedence: explicit user decision > official product source > verified behavior > project docs > existing copy > inference.
3. **Risk gate:** low local microcopy may use local evidence; medium requires flow/locale/claim reconciliation; high pricing/paywalls/security/privacy/commercial/legal/trust/account-access copy requires declared or verified material context.
4. **Truth and quality gates:** preserve variables, prices, limits, dates, permissions, and behavior; unknown truth is blocked; run all eight checks in [language-quality.md](language-quality.md).
5. **Composition gate:** for compose, map each proposed string to a visible surface element and evidenced state/transition. Do not add recovery, loading, entitlement, or success claims unless behavior is declared or verified.
6. **Scope and delivery gates:** distinguish defects from optional improvements, preserve intentional copy, and stop for behavior, legal, pricing, consent, accessibility, or policy decisions.

For a blocked high-risk request, return an incomplete-context diagnosis and do not invent claims.

## Cache and ledger contract

Context discovery may reuse a cached fragment only when the normalized query, scope, locale/risk classification, and content hash of every consulted source match. Record cache hits in `discovery_ledger.consulted` or `queries` with `cache: reused` and the source hash; do not reread unchanged fragments merely to restate them. Invalidate the entry when a source hash, requested scope, locale, risk, user instruction, or authoritative precedence changes, or when the user requests a fresh audit. Record invalidation reason and the replacement hash in `discovery_ledger.expansions`.

A cache is an efficiency aid, not evidence: preserve source status and confidence, and never reuse a stale or conflicted high-risk claim. A run ledger should identify consulted sources, grouped exclusions, query hashes, cache decisions, and any expansion beyond the initial budget.

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

First present a 2–5 sentence human summary. The structured result remains one object with exactly these 14 top-level keys:

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
  execution_profile: balanced
  discovery_ledger:
    consulted: []
    queries: []
    not_consulted: []
    expansions: []
```

`project_context.status` is `complete`, `partial`, `conflicted`, or `missing`; `stage` is `new`, `mid-project`, `nearly-complete`, or `unknown`. Source status is `declared`, `verified`, `observed`, `inferred`, `conflicted`, or `unknown`. Keep all existing top-level fields even when empty; the nested ledger does not add a top-level key.

## Locale and tone declaration

Always state whether language and locale were requested, inferred, or defaulted. Keep locale, tone, register, intent, audience, and channel separate; translation is not a tone decision.
