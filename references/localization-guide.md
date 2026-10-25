# Localization guide

## Supported locales

| Locale | Use |
|---|---|
| es-419 | Neutral Latin American Spanish; default for inferred Spanish. |
| es-MX | Mexican Spanish when explicitly requested or established by the project. |
| en-US | American English; default for inferred English. |
| en-GB | British English when explicitly requested or established by the project. |

If locale is unspecified, infer the language from the input or project evidence. Default Spanish to es-419 and English to en-US. Always declare whether the locale was requested, inferred, or defaulted. If the evidence is ambiguous, ask one blocking question only when the choice changes meaning, eligibility, price, or legal interpretation.

## Localization checks

- Preserve interpolation names, markup, keyboard labels, and accessibility semantics.
- Use locale-aware date, number, currency, unit, plural, and capitalization conventions.
- Do not translate product names, route names, code identifiers, or protected terminology without evidence.
- Keep a source-language concept stable across all states; avoid translating the same concept two ways.
- Use sentence case unless the product’s established convention requires otherwise.
- Avoid literal translation: translate the user intent, action, consequence, and level of certainty.
- Flag missing or contradictory locale keys instead of silently falling back when the fallback could mislead.
- Review both sides of bilingual UI; never use the presence of a language toggle as permission for mixed active copy.

## Locale declaration example

```yaml
language_locale:
  language: Spanish
  locale: es-419
  assumption: "Language inferred from the source text; Spanish locale defaulted to es-419 because no regional locale was supplied."
```
