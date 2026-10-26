# Community testing protocol

This lightweight protocol helps contributors compare a baseline with Adaptive Product Language without turning one local run into a benchmark claim.

## One paired comparison

1. Choose one concrete, synthetic or privacy-safe prompt and its required context.
2. Run the baseline without the skill and the skill condition with the skill loaded.
3. Keep the model, model version, system/developer prompt, user prompt, context, tools, temperature, and other settings the same.
4. Randomize or record condition order when practical.
5. Compare only the visible-copy outputs for quality. Do not score hidden reasoning, telemetry, or report metadata as product copy.

A single paired comparison is useful for finding regressions, invented claims, or workflow differences. It is not a statistically powered experiment, and this protocol does not promise statistical significance.

## Evidence and claim safety

Save the exact prompts, context, outputs, settings, date, and host. Redact private material before sharing. Quote the smallest relevant output fragment and explain the evidence for each quality observation. Treat unsupported claims, omissions, locale drift, and behavior changes as separate findings. Do not treat shorter text, a preference, or a single successful run as proof of quality.

## Separate quality from efficiency

- **Quality:** visible-copy correctness, evidence fidelity, locale/register, clarity, and absence of critical regressions.
- **Efficiency:** observed bytes, tokens, elapsed time, tool calls, files read, or other host telemetry.

Record these in separate sections. Bytes are not tokens, and missing telemetry must be reported as unavailable rather than estimated. A quality improvement does not imply an efficiency improvement, and vice versa.

## Report template

```markdown
# Community test: <short name>

- Date:
- Host/provider/model/version:
- Skill version or commit:
- Locale/domain/surface:
- Prompt and context source:
- Settings held constant:
- Baseline output:
- Skill output:

## Quality observations

- Evidence-backed improvement:
- Evidence-backed regression or remaining issue:
- Critical-regression check:

## Efficiency observations

- Bytes:
- Tokens (only if observed):
- Elapsed time (only if observed):
- Other telemetry:

## Claim boundary

State what this one paired comparison suggests, what it does not establish, and what should be tested next. Do not claim statistical significance or general superiority from one run.
```

For larger or repeated studies, use the maintainer benchmark protocol in [`../benchmarks/README.md`](../benchmarks/README.md) rather than silently extending this lightweight comparison.
