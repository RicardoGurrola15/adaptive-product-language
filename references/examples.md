# Examples

These examples are illustrative; verify the actual action and product truth before reuse.

## CTA and recovery

| Context | Spanish (es-419) | English (en-US) | Why |
|---|---|---|---|
| Save a draft | `Guardar borrador` | `Save draft` | Names the persistent outcome. |
| Preview only | `Ver vista previa` | `Preview` | Does not promise publication. |
| Retry a failed request | `Intentar de nuevo` | `Try again` | Gives a concrete recovery action. |
| Missing required field | `Ingresa tu ciudad para continuar.` | `Enter your city to continue.` | Identifies the value and consequence. |

## Pricing transparency

Weak:

- `Oferta exclusiva`
- `Unlock now`
- `Desde $9`

Stronger when truthful:

- `Plan Plus — $9 USD al mes. Cancela cuando quieras.`
- `Plus plan — $9 USD/month. Cancel anytime.`

If currency, cadence, eligibility, or renewal is not authoritative, do not fill the gap with a confident sentence. Create a blocking finding instead.

## Onboarding

Weak:

- `¡Todo listo!`

Stronger:

- `Publica tu primer anuncio en tres pasos. Puedes guardarlo como borrador y continuar después.`
- `Publish your first listing in three steps. You can save it as a draft and continue later.`

Only use the second sentence if draft persistence exists.

## Non-coercive paywall

- `Para publicar más de 3 anuncios, elegí un plan.`
- `To publish more than 3 listings, choose a plan.`

Provide the actual plan price, cadence, limits, eligibility, and an equivalent decline or return action in the surrounding UI. Do not use `No, I want fewer opportunities` or equivalent guilt language.

## Copy that should remain unchanged

Input:

- `Guardar cambios`
- `Save changes`

If the control actually persists edits, the terms are consistent with the glossary, and both locales meet the checks, return `findings: []` and explain that no change is warranted.

## Exact finding example

```yaml
id: PL-012
priority: urgent
category: marketing-transparency
scenario: pricing/paywalls/monetization
location: src/Plans.tsx:72
current_text: "$9; Save 30%"
problem: "The offer cannot be evaluated without unit, timing, and eligibility."
evidence: "The card says '$9' and 'Save 30%' but omits cadence and eligibility."
proposed_change: "State the authoritative currency, cadence, eligibility, and discount basis."
expected_impact: "Users can evaluate the paid option without guessing material terms."
confidence: 0.97
blocking_question: "What are the authoritative currency, cadence, eligibility, and discount terms?"
```
