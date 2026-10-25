# Context drift audit

Use this read-only operation for nearly-complete projects before launch copy polish.

## Compare

| Evidence | Check |
|---|---|
| Product context | Current decisions, audience, locale, terminology, and approved claims. |
| Code and tests | Verified behavior, entitlements, state transitions, and recovery actions. |
| Pricing and policy sources | Currency, cadence, eligibility, renewal, consent, privacy, and legal disclosures. |
| Shipped copy | Active UI, landing, SEO, email, help, and locale variants. |

## Report

For each drift item, cite source paths and evidence state, classify it as stale context, unsupported copy, source conflict, locale drift, or terminology drift, and state whether it blocks release. Do not remediate without explicit bounded authorization. High-risk drift remains blocked until declared or verified context resolves it.

## Exit criteria

- All high-risk claims have declared or verified context.
- Conflicts and missing facts appear in `project_context`.
- Existing authoritative glossaries and guides are reused.
- No change is claimed complete without authorization and evidence.
