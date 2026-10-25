# Scenario matrix

These are the twelve stable product-context IDs. Use them as the `scenario` value in findings and report which context shaped a decision.

| ID | Product context | Required behavior |
|---|---|---|
| attraction/discovery | Attraction and discovery | Make the value, destination, and next exploration action clear without overstating what users will find. |
| value proposition | Value proposition | State the user benefit and meaningful outcome without unsupported promises or vague superiority. |
| trust/security/privacy | Trust, security, and privacy | Explain handling, permissions, and safeguards accurately without implying protections that are not verified. |
| product communication | Product communication | Keep announcements, labels, notifications, and promotional language clear, consistent, and truthful. |
| onboarding/activation | Onboarding and activation | Clarify first value, next step, effort, and optionality without inventing capabilities. |
| registration/login/recovery | Registration, login, and recovery | Name the account action and recovery path accurately, including relevant status and next steps. |
| forms/data capture | Forms and data capture | Identify requested data, requiredness, format, purpose, and resulting action without ambiguity. |
| pricing/paywalls/monetization | Pricing, paywalls, and monetization | State authoritative price, cadence, limits, eligibility, renewal, and equivalent decline or return paths. |
| errors/recovery | Errors and recovery | Explain the problem and offer only recovery actions that actually exist. |
| system states | System states | Cover loading, empty, offline, permission, rate-limit, success, and partial-failure states without technical leakage. |
| help/support/education | Help, support, and education | Provide accurate guidance, terminology, escalation paths, and learning context appropriate to the user state. |
| legal/institutional/compliance | Legal, institutional, and compliance | Preserve authoritative meaning and required disclosures; escalate legal or policy uncertainty instead of rewriting it. |

## Scenario handling

An audit fixture scenario is a separate test case and is not a product-context ID. A context is a test of judgment, not permission to rewrite. A finding can be optional or absent when the surface already meets the requirement. A behavior-dependent issue must not be disguised as a linguistic issue.
