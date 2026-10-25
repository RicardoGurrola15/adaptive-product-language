## 2026-10-25

- Added portable paired quality and profile-cost benchmark fixtures and aggregator.

# Changelog

All notable changes to Adaptive Product Language are documented here.

## [0.4.0] - 2026-10-25

### Added

- Added explicit `light`, `balanced` (default), and `performance` execution profiles, separate from operation mode, with bounded budgets and profile reporting in `project_context`.

### Changed


- Documented the package portability model across Agent Skills-compatible or Markdown-capable hosts, including host-specific installation/discovery and optional Codex/OpenAI metadata.

## [0.3.0] - 2026-10-25

### Changed

- Added progressive investigation budgets: classify, inventory, targeted search, relevant fragments, risk-based sufficiency, and explicit stop conditions.
- Added the nested `project_context.discovery_ledger` for consulted evidence, queries, grouped exclusions, and justified expansions without changing the top-level contract.
- Set a sequential bounded agent as the default for broader exploration or multi-file writing; prohibited parallel explorers for one audit.
- Required a short human product summary before the unchanged structured result, keeping paths and lines as evidence rather than the primary explanation.
- Preserved read-only auditing, source precedence, locale/context rules, all 14 output keys, and the exact 12-key finding schema.

## [0.2.0] - 2026-10-25

### Added

- Formal Context Layer with canonical and fallback source discovery, evidence states, confidence, precedence, and reusable template asset.
- Context Gate risk tiers that block high-risk claims without declared or verified context.
- Bootstrap, reconciliation, and drift-audit operations with glossary/guide reuse detection.
- `project_context` as the sole addition to the structured output contract, preserving the existing 13 top-level keys and exact 12-key finding schema.
- Context-focused declarative evaluation fixtures.

## [0.1.0] - 2026-10-25

### Added

- LLM-first generation, review, read-only audit, and explicitly authorized remediation modes.
- Locale defaults and assumptions for es-419, es-MX, en-US, and en-GB.
- Eight-dimensional quality checks, finding schema, priority system, discovery protocol, and declarative fixtures.
