# Contributing

Contributions should improve the skill's evidence handling, language quality, portability, or documentation without inventing product facts. Keep changes bounded and explain what a reviewer can verify.

## Report a failure

Open an [issue](https://github.com/RicardoGurrola15/adaptive-product-language/issues) with:

- the host, model, locale, and skill version;
- the smallest prompt and relevant context needed to reproduce the result;
- the expected behavior and the observed visible copy or report;
- whether the failure was an unsupported claim, missed context, locale problem, routing problem, or remediation-boundary problem; and
- focused checks already run.

Remove secrets, personal data, customer content, proprietary product details, and identifying URLs before posting. If the material cannot be safely sanitized, describe the pattern instead of attaching it.

## Propose a fixture

Add a small, self-contained fixture only when it captures a reusable behavior. Include the surface, audience, locale, risk, verified context, constraints, invariants, and expected findings. Explain the failure the fixture protects against. Do not add a fixture that depends on a private repository, hidden model behavior, or an unverifiable product claim.

## Add a locale or domain

Document the intended locale or domain boundary first. Preserve product meaning, behavior, legal intent, terminology, and locale neutrality where required. Add only the references and fixtures needed for the bounded case; do not broaden activation or add generic vocabulary rules without evidence.

## Preserve privacy

Use synthetic or public examples. Never commit secrets, credentials, customer data, private URLs, unpublished pricing, or identifying user content. Review diffs and generated artifacts before sharing them. Keep local benchmark results and reports ignored unless an intentionally curated, privacy-reviewed summary belongs in the repository.

## Run focused checks

From the repository root:

```bash
python3 -m py_compile benchmarks/*.py
python3 -m unittest discover -s benchmarks -p 'test_*.py'
```

For documentation-only changes, also verify links and paths with shell checks such as:

```bash
while read -r path; do test -e "$path" || exit 1; done < <(grep -oE '\]\([^)#]+\)' README.md CONTRIBUTING.md docs/*.md | sed -E 's/^\]\(|\)$//')
```

Do not run real model calls or benchmarks as a substitute for focused checks unless the experiment is explicitly authorized and follows [`docs/community-testing.md`](docs/community-testing.md).

## Claims and review

One run can reveal a useful failure or process signal, but it cannot establish general superiority, statistical significance, or stable model behavior. Report quality and efficiency separately, include the protocol and caveats, and avoid claiming more than the evidence supports.
