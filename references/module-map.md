# Module map

Load modules on demand. `SKILL.md` is the router; these references are the payload.

| Module | Reference | Purpose | Load when |
|---|---|---|---|
| Routing and formal contract | `decision-system.md` | Modes, gates, precedence, schemas | Audit, remediate, formal localize/context, or explicit formal request |
| Progressive discovery | `context-discovery.md` | Budgets, stop conditions, ledger | Audit, remediation, context, or evidence expansion |
| Profiles | `execution-profiles.md` | Cost/depth and cache reporting | Every request after route classification |
| Composition | `contextual-adaptation.md`, `language-quality.md` | Context-fit and quality checks | Every `compose` request |
| Component/form/accessibility | `component-rules.md` | Control, form, validation, and accessible-state language | Only when compose/improve scope includes components, forms, or accessibility |
| Quality | `language-quality.md`, `anti-patterns.md`, `contextual-adaptation.md` | Defect, contextual-generic, and dark-pattern checks | `improve`, `audit`, or `remediate`; load contextual adaptation for `improve` only |
| Localization | `localization-guide.md`, `terminology.md`, `tone-and-register.md` | Locale, terms, register | `localize` or bilingual work |
| Context | `project-context.md`, `context-drift-audit.md` | Declared facts, reconciliation, drift | `context` or a material-claim conflict |
| Remediation | `audit-and-remediation.md` | Authorization and bounded edits | `remediate` only |
| Examples | `examples.md` | Non-normative examples | Only when an example is needed |

Do not load unrelated modules merely because they exist. Normal compose never loads `decision-system.md`; it returns visible copy rather than report fields. Do not load benchmark files for normal work. Benchmark prompts, fixtures, telemetry, and scoring remain isolated under `benchmarks/` and are maintainer-only.
