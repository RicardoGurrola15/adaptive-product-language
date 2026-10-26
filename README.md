# Adaptive Product Language

Adaptive Product Language routes contextual product-language work for UI screens, components, forms, flows, marketing, and explicit login/account requests. It excludes visual-only styling and loads only the references needed for the selected intent.

It is an Agent Skills-compatible Markdown package: the repository is usable as a standalone checkout, and the skill can be copied into a host's project-local skill directory.

## Quick start

1. Install the package using one of the paths below.
2. Invoke `adaptive-product-language` for a language task.
3. Name the surface, user action, locale, and intent: `compose`, `improve`, `audit`, `remediate`, `localize`, or `context`.
4. Provide the verified product context or identify what is unknown. The skill will investigate only enough evidence for the selected risk.

Example:

> Compose a Spanish CTA for saving search filters. Preserve the verified behavior and do not imply that matching results already exist.

## Installation

### Standalone repository

The repository root is itself a valid skill package. Point a host that supports standalone Agent Skills to the checkout's root [`SKILL.md`](SKILL.md). Keep the `references/` and `assets/` directories beside it because the skill uses relative links.

```bash
git clone https://github.com/RicardoGurrola15/adaptive-product-language.git
cd adaptive-product-language
# Configure the host to discover this directory, or load ./SKILL.md explicitly.
```

### Project-local installation

For a project-local install, copy the package into `.agents/skills/adaptive-product-language/` so that the destination contains `SKILL.md`, `references/`, and `assets/`:

```bash
mkdir -p .agents/skills
git clone https://github.com/RicardoGurrola15/adaptive-product-language.git \
  .agents/skills/adaptive-product-language
```

If the repository is already checked out elsewhere, copy the repository contents into that same destination rather than copying only `SKILL.md`.

## Host portability

The core package is plain Markdown plus local references and is intended for Codex, Claude, Gemini CLI, and other Agent Skills-compatible or Markdown-capable hosts. Discovery and invocation syntax are host-specific:

- **Codex:** install in a configured skills directory or project-local `.agents/skills/`; [`agents/openai.yaml`](agents/openai.yaml) is optional Codex/OpenAI metadata.
- **Claude:** place the package where the host discovers skills, or load the root `SKILL.md` explicitly with its sibling references.
- **Gemini CLI:** place it in the host's supported skills directory or invoke the root `SKILL.md` explicitly.
- **Other agents:** use any supported Agent Skills directory; otherwise provide `SKILL.md` and preserve its relative `references/` and `assets/` paths.

The package has no runtime, private API, MCP, framework, or model-provider dependency. GitHub is distribution; it is not a universal installer.

## Normal modes

| Intent | Behavior |
|---|---|
| `compose` | Generate only the requested visible copy, using evidenced states and declared context. |
| `improve` | Review or improve existing copy; do not edit files unless remediation is explicitly bounded. |
| `audit` | Read-only inspection of language quality, drift, unsupported claims, and context gaps. |
| `remediate` | Apply only explicitly named findings and paths; preserve behavior, pricing, legal meaning, and unrelated copy. |
| `localize` | Adapt language while preserving product facts, behavior, and locale meaning. |
| `context` | Establish or reconcile product-language context without inventing facts. |

Execution depth is separate from intent. Use `light`, `balanced` (default), or `performance`; these profiles control investigation depth, not model reasoning or guaranteed speed.

## Context file

For a project with durable product facts, use `.product-language/context.yaml` as the authoritative context location. Start from [`assets/context-template.yaml`](assets/context-template.yaml), then declare only verified product, audience, behavior, pricing, trust, locale, terminology, and policy information. The template is a proposal: the skill must not create or treat it as truth without project evidence.

## Audit and remediation

Audits are read-only. The skill inventories relevant candidates, searches targeted evidence, records what it consulted, and stops when evidence is sufficient. It blocks or reports unsupported product, pricing, legal, consent, or behavior claims instead of guessing.

Remediation is opt-in and bounded. Name the findings and paths to change; the skill must preserve behavior and unrelated files, then report changed paths and validation. Normal compose requests return visible copy only. Audit, remediation, localization/context, or an explicit formal request returns the structured report contract documented in [`references/decision-system.md`](references/decision-system.md).

## Limitations

The skill cannot establish authoritative product policy, legal requirements, pricing truth, runtime behavior, accessibility conformance, or user research findings from copy alone. It cannot replace product, legal, localization, accessibility, or engineering review. When evidence is missing or conflicting, expect an assumption, an incomplete-context result, or a request for authoritative sources rather than an invented claim.

## Validation and benchmark caveat

Run focused local checks without making model calls:

```bash
python3 -m py_compile benchmarks/*.py
python3 -m unittest discover -s benchmarks -p 'test_*.py'
```

Do not run a real model benchmark as ordinary validation. Benchmark outputs require a fixed paired protocol, blinded quality evaluation, and observed telemetry. Text length or byte differences alone are not quality evidence. See [`benchmarks/README.md`](benchmarks/README.md), the [community testing protocol](docs/community-testing.md), and the [preliminary observations](docs/benchmark-results.md).

## Contributing

Start with [`CONTRIBUTING.md`](CONTRIBUTING.md). Report a failure with the smallest reproducible prompt and context, propose privacy-safe fixtures, and separate quality observations from efficiency measurements. See the [issue tracker](https://github.com/RicardoGurrola15/adaptive-product-language/issues) and [pull requests](https://github.com/RicardoGurrola15/adaptive-product-language/pulls).
