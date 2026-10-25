# Context discovery

## Progressive investigation protocol

Classify mode, surface, flow, locale, channel, risk, and material claims before opening content. Then: inventory candidate routes/files without reading them in full; run grouped, hypothesis-led searches; read only fragments around relevant results; evaluate sufficiency; stop; and expand only for a contradiction, material claim, real dependency, or an explicit request. Repeating searches or rereading broad sources is not investigation.

| Risk / mode | Initial budget | Stop condition |
|---|---|---|
| point / low | 1–3 files and 1 targeted search | Local context and restrictions support copy; no product facts are introduced. |
| medium | Up to 5 candidate files, 3 queries, and 3 initial fragments | Flow, locale/glossary, and highest claim source agree; searches find no contradiction. |
| high / audit | Inventory first; relevant sources only and up to 5 initial queries | Each material claim is declared or verified; otherwise return a blocked diagnosis. |

Do not read all documentation by default. If the user explicitly asks for “all documentation,” comply and record it as an explicit expansion.

## Discovery ledger

Place a compact `discovery_ledger` inside `project_context`; it never changes the 14 top-level keys. It is required for audit and remediation and optional/compact for point work:

```yaml
discovery_ledger:
  consulted:
    - target: "src/Checkout.tsx"
      range: "88-114"
      method: "search fragment"
      purpose: "Review renewal claim"
  queries:
    - query: "renewal OR billing OR monthly"
      scope: "src/, locales/"
      result: "One visible price and no cadence source"
  not_consulted:
    - area: "Unrelated admin and test directories"
      reason: "Outside checkout flow and no claim dependency"
  expansions:
    - reason: "Explicit user request to inspect all documentation"
```

Group exclusions; do not enumerate irrelevant files. Record every extra read, query, or agent after the initial budget and why it was necessary.

## Source order

Look first for canonical `.product-language/context.yaml`, then `product-language.context.yaml`, `docs/product-language-context.md`, brand docs, glossaries, localization files, pricing docs, code/tests, and existing copy—but only when the classified flow or a claim calls for that source. Classify each consulted source with an evidence state and confidence; precedence is defined in [project-context.md](project-context.md).

## Operations

| Project stage | Operation | Result |
|---|---|---|
| new | Context bootstrap | Propose context from declared facts and marked unknowns; offer the reusable template, not a repository file. |
| mid-project | Context reconciliation | Reuse relevant glossaries/guides, compare consulted sources, and record conflicts. |
| nearly-complete | Context drift audit | Compare relevant copy, behavior, policies, locales, and pricing; report drift before polish. |

## Practical examples

- **Spanish principle:** `Texto sin contexto es ser errático.`
- A visible `$9` card is `observed`, not authoritative pricing; search for declared or verified cadence, currency, eligibility, and renewal terms before expanding.
- A glossary already naming a concept is evidence to reuse; do not create a second glossary merely to standardize copy.
