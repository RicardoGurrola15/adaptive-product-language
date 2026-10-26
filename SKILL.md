---
name: adaptive-product-language
description: "Trigger: product language, UX copy, localization, copy audit, bilingual UI, CTA, pricing, onboarding, errors, login, screens, components, forms, flows, or marketing copy. Route contextual language work; do not activate for visual-only work."
license: Apache-2.0
metadata:
  author: "casamapa"
  version: "0.9.0"
---

## Activation Contract

Activate for user-facing language in UI screens, components, forms, flows, marketing, or explicit login/sign-in/registration/recovery requests. Treat language as product behavior: **texto sin contexto es ser errático**. Do not activate for visual-only styling, spacing, color, icons, motion, layout, or assets without a language decision; mixed requests stop at the language boundary.

## Router

Classify the request, then load only the matching module from [module-map](references/module-map.md) using [intent-routing](references/intent-routing.md):

| Intent | Route | Authorization |
|---|---|---|
| Compose new coordinated copy | `compose` | Generate only evidenced states |
| Improve existing copy | `improve` | Read-only unless bounded remediation is explicit |
| Inspect quality or drift | `audit` | Read-only |
| Apply named findings | `remediate` | Explicit paths/findings only |
| Change language/locale | `localize` | Preserve meaning and product facts |
| Establish or reconcile context | `context` | Proposal/reconciliation; do not invent facts |

`benchmark` is maintainer-only and never part of normal routing. Build a context card for every compose request: product, audience, domain, surface, objective, risk, locale, and flow stage. Mark unknown material facts and do not fill them with generic language. Preserve behavior, prices, limits, legal meaning, consent, variables, intentional copy, and es-419 neutrality. Never infer downstream effects or unsupported claims. For `compose` and `improve`, load [contextual adaptation](references/contextual-adaptation.md): adapt to evidenced context, not a universal word list; treat clichés as warning signals, never bans or required vocabulary.

## Profiles and output

Select `light`, `balanced` (default), or `performance` separately from intent. Follow the budgets and cache rules in [execution profiles](references/execution-profiles.md). Normal `compose` returns visible copy only in the requested structure; it omits diagnosis, rationale, findings, project context, and telemetry unless a formal report is explicitly requested. Audit, remediation, localization/context reports, or an explicit formal request use the exact 14-key contract and unchanged 12-key finding schema in [decision system](references/decision-system.md). Human summaries and prose values MUST follow the requested or inferred locale; fixed schema keys and route identifiers may remain English. Never produce an English human summary for `es-419`. Keep execution telemetry separate from copy and never expose it as visible product language.

## References

- [Intent routing](references/intent-routing.md)
- [Module map](references/module-map.md)
- [Decision system](references/decision-system.md) — formal reports only
- [Context discovery](references/context-discovery.md)
- [Execution profiles](references/execution-profiles.md)
- [Localization](references/localization-guide.md)
- [Language quality](references/language-quality.md)
- [Contextual adaptation](references/contextual-adaptation.md) — `compose` and `improve` only
