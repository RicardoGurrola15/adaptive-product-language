# Intent routing

Classify intent before loading domain guidance. The first matching route wins: explicit bounded remediation, existing-surface audit, localized change, coordinated composition, point improvement, then context work. If the request is ambiguous, ask one blocking question rather than loading every module.

| Route | Signals | Load first | Stop/authorization rule |
|---|---|---|---|
| `compose` | create a screen, component, form, flow, or marketing section | `contextual-adaptation`, `language-quality` | Return visible copy only; map sections to declared constraints and do not invent claims. |
| `improve` | rewrite, polish, clarify, shorten, or strengthen existing copy | `language-quality`, `tone-and-register`, `terminology` | Point work stays local; no remediation without explicit bounded authorization. |
| `audit` | review, inspect, find issues, drift, consistency, or accessibility language | `context-discovery`, `decision-system`, `audit-and-remediation` | Read-only; use the formal report contract. |
| `remediate` | apply approved fixes or named findings | `audit-and-remediation`, `decision-system` | Change only authorized paths/findings; verify only affected scope. |
| `localize` | translate, adapt locale, bilingual copy, es-419/en-US | `localization-guide`, `terminology`, `tone-and-register` | Preserve meaning, variables, facts, and locale requirements; report assumptions. |
| `context` | bootstrap, reconcile, or drift-audit product-language context | `project-context`, `context-discovery`, `context-drift-audit` | Propose facts and unknowns; never create context files unless explicitly requested. |

## Shared gates

1. Exclude visual-only requests before loading any language module.
2. For compose, retain product, audience, domain, surface, objective, risk, locale, and flow stage as active constraints.
3. Load the smallest matching reference set, then expand only for contradiction, dependency, material claim, or explicit request.
4. `component-rules.md` is only for component, form, or accessibility language; it is not a default marketing/landing dependency.
5. Normal compose never loads `decision-system.md`; use it only for formal audit, remediation, localization/context, or an explicitly formal response.
6. Normal compose returns copy only. Keep diagnosis, rationale, findings, project context, and execution telemetry out of visible copy.

`benchmark` is not a user route. Maintainers may invoke isolated benchmark tooling directly; benchmark code must not be loaded into normal skill instructions or used as product evidence.
