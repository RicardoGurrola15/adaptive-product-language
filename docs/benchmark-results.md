# Preliminary benchmark observations

These are preliminary local observations from the same contextual phone landing prompt. They are recorded for transparency, not as a validated benchmark or a claim of general superiority. The comparisons are one sample per model; byte counts are UTF-8 output sizes, not token counts.

## Observations

| Model | Baseline | Skill | Difference | Qualitative observation |
|---|---:|---:|---:|---|
| Gemini 3.8 Flash | 2912 bytes | 2663 bytes | ~8.5% shorter | The skill output qualitatively improved avoidance of invented product features. |
| Claude Sonnet 4.6 Thinking | 3289 bytes | 3034 bytes | ~7.8% shorter | The skill avoided invented product examples and prices, but still invented filters, photos, battery, reparation, and support details. |

## Interpretation boundary

The observations suggest a promising process signal: the skill may help constrain unsupported product-language claims in this prompt. They do not prove superiority, quality improvement in general, statistical significance, or a stable efficiency advantage. The known model-dependent claim drift is material: Claude still produced unsupported details even after avoiding some other inventions.

The byte differences should not be reported as token savings or latency improvements. No token or latency data is claimed here. Further testing should use the paired protocol, repeated cases, blinded quality evidence, and observed telemetry described in [`community-testing.md`](community-testing.md) and [`../benchmarks/README.md`](../benchmarks/README.md).
