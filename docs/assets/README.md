# Benchmark chart assets

These repository-native SVGs summarize the validated paired observations documented in [`../benchmark-results.md`](../benchmark-results.md):

- [`output-bytes-comparison.svg`](output-bytes-comparison.svg) compares UTF-8 output bytes for the two model observations.
- [`codex-quality-observations.svg`](codex-quality-observations.svg) shows the observed Codex quality ties.

## Provenance and update procedure

1. Verify the source observations and sample counts in `docs/benchmark-results.md`.
2. Update the SVG values, labels, accessible `<title>`, and `<desc>` together.
3. Keep the caveats visible: bytes are not tokens; observations are not statistical proof; one-sample Codex ties do not establish general superiority.
4. Run the local documentation checks described in the repository README.

Do not update these figures from unverified runs, synthetic outputs, or unobserved benchmark claims. Keep chart edits limited to the documented observations and preserve readable contrast and text labels.
