# Context discovery

## Progressive investigation protocol

Classify route/mode, surface, flow, locale, channel, audience, risk, behavior, and material claims before opening content. Then inventory candidate routes/files without reading them in full; run grouped, hypothesis-led searches; read only fragments around relevant results; evaluate sufficiency; stop; and expand only for a contradiction, material claim, real dependency, or explicit request. Repeating searches or rereading broad sources is not investigation.

| Risk / route | Initial budget | Stop condition |
|---|---|---|
| point / low / compose-local | 1–3 files, 1 targeted query, 1–2 fragments | Local context and restrictions support copy; no product facts are introduced. |
| medium | Up to 5 candidate files, 3 queries, 3 initial fragments | Flow, locale/glossary, behavior, and highest claim source agree; searches find no contradiction. |
| high / audit | Inventory first; up to 8 relevant files and 5 initial queries/fragments | Each material claim is declared or verified; otherwise return a blocked diagnosis. |

The selected execution profile may narrow these budgets, but never removes a high-risk gate. An explicit request for all documentation is honored and recorded as an expansion.

## Discovery ledger

Place a compact `discovery_ledger` inside `project_context`; it never changes the 14 top-level keys. It is required for audit and remediation and optional/compact for point/compose work:

```yaml
discovery_ledger:
  consulted:
    - target: "src/Checkout.tsx"
      range: "88-114"
      method: "search fragment"
      purpose: "Review renewal claim"
      source_status: observed
      content_hash: sha256:...
      cache: miss
  queries:
    - query: "renewal OR billing OR monthly"
      query_hash: sha256:...
      scope: "src/, locales/"
      result: "One visible price and no cadence source"
      cache: reused
  not_consulted:
    - area: "Unrelated admin and test directories"
      reason: "Outside checkout flow and no claim dependency"
  expansions:
    - reason: "Explicit user request to inspect all documentation"
    - reason: "Source hash changed; invalidated prior fragment"
```

Hash source bytes and normalized queries with SHA-256 when a cache or resumable ledger is used. Do not treat a hash as evidence by itself. Reuse is valid only when source hash, query hash, scope, locale, risk, and precedence inputs are unchanged. Invalidate on any mismatch, on an authoritative conflict, or on a requested fresh read; record both the invalidation reason and replacement hash.

## Source order

Look first for canonical `.product-language/context.yaml`, then `product-language.context.yaml`, `docs/product-language-context.md`, brand docs, glossaries, localization files, code/tests, and existing copy—but only when the classified flow or a claim calls for that source. Classify each consulted source with an evidence state and confidence; precedence is explicit user decision > official product source > verified behavior > project docs > existing copy > inference. A conflict at a higher-precedence source blocks the lower-precedence claim.

## Operations

| Project stage | Operation | Result |
|---|---|---|
| new | Context bootstrap | Propose context from declared facts and marked unknowns; offer the reusable template, not a repository file. |
| mid-project | Context reconciliation | Reuse relevant glossaries/guides, compare consulted sources, and record conflicts. |
| nearly-complete | Context drift audit | Compare relevant copy, behavior, policies, locales, and pricing; report drift before polish. |

## Composition and login screens

For `compose`, map visible elements to states and behavior before writing: heading/value, supporting explanation, fields, primary action, secondary action, validation, loading, success, and recovery only when present or verified. For login/registration/recovery screens, verify the available access method and recovery behavior; do not add social login, passwordless access, account creation, or persistence claims without evidence.

## Practical examples

- **Spanish principle:** `Texto sin contexto es ser errático.`
- A visible `$9` card is `observed`, not authoritative pricing; search for declared or verified cadence, currency, eligibility, and renewal terms before expanding.
- A glossary already naming a concept is evidence to reuse; do not create a second glossary merely to standardize copy.
- A visual-only styling request has no language surface and should not activate this skill.
