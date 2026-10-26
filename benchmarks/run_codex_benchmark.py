#!/usr/bin/env python3
"""Run the read-only Codex benchmark matrix with resumable checkpoints.

The runner records execution observations only. It never assigns quality scores;
use evaluate_results.py for blind scoring.
"""
import argparse
import hashlib
import json
import pathlib
import random
import subprocess
import sys
import tempfile
import time

from benchmark_protocol import BENCHMARK_PROTOCOL_VERSION, require_current_protocol

HERE = pathlib.Path(__file__).resolve().parent
SKILL = HERE.parent
DEFAULT_PROJECTS = pathlib.Path(tempfile.gettempdir()) / "apl-basic-projects"
CONDITIONS = ("baseline", "light", "balanced", "performance")
SINGLE_RUN_CASE = "es419_cta"
QUALITY_DIMENSIONS = (
    "completeness", "context_fit", "specificity", "coherence",
    "naturalness_non_robotic_rhythm", "commercial_congruence", "cta_clarity",
    "locale_quality", "claims_boundary",
)
TELEMETRY_FIELDS = (
    "input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens",
    "elapsed_ms", "tool_calls", "stage_timings",
    "candidate_files", "files_read", "references", "searches", "context_bytes",
    "escalations", "cache_hit", "cache_miss", "profile", "stop_reason",
    "interruptions", "changed_text_count", "preserved_text_count",
)
FIRE_TESTS = {
    "casamapa": "/Volumes/intento1/Repos/casamapa",
    "noura": "/Volumes/intento1/Repos/noura",
    "fenix": "/Volumes/intento1/Repos/Fenix",
    "futkards": "/Volumes/intento1/Repos/futkards",
}
PILOT_CASES = HERE / "cases.yaml"
PILOT_FIELDS = (
    "case_id", "scenario", "locale", "title", "context", "audience", "surface", "behavior",
    "prompt", "expected_constraints", "expected_findings", "positive_control", "composition", "rubric_applicability", "conditions",
)
PILOT_OPTIONAL_FIELDS = ("invariants", "copy_only", "visible_sections")

TOOL_CALL_ITEM_TYPES = {"command_execution", "file_search", "mcp_tool_call", "function_call", "web_search", "computer_call", "tool_call", "custom_tool_call"}
FORMAL_CONTRACT_KEYS = (
    "mode", "diagnosis", "detected_problems", "main_proposal", "alternatives",
    "language_locale", "tone_register", "rationale", "confidence", "assumptions",
    "blocking_questions", "findings", "remediation", "project_context",
)
LANGUAGE_LOCALE_KEYS = ("language", "locale", "assumption")
PROJECT_CONTEXT_KEYS = (
    "status", "stage", "sources", "missing", "conflicts", "assumptions",
    "confidence", "execution_profile", "discovery_ledger",
)
DISCOVERY_LEDGER_KEYS = ("consulted", "queries", "not_consulted", "expansions")
FINDING_KEYS = (
    "id", "priority", "category", "scenario", "location", "current_text",
    "problem", "evidence", "proposed_change", "expected_impact", "confidence",
    "blocking_question",
)
COMPOSE_REFERENCES = (
    "references/contextual-adaptation.md",
    "references/language-quality.md",
)


def digest(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def ensure_basic_projects(path):
    first_context = next(iter(sorted(path.glob("basic-*/context.yaml"))), None) if path.exists() else None
    current_schema = first_context and "surface" in first_context.read_text(encoding="utf-8") and "invariants" in first_context.read_text(encoding="utf-8")
    if not path.exists() or len(list(path.glob("basic-*"))) < 30 or not current_schema:
        subprocess.run([sys.executable, str(HERE / "generate_basic_projects.py"), "--output-dir", str(path), "--clean"], check=True)
    return sorted(directory for directory in path.glob("basic-*") if (directory / "prompt.txt").exists())


def parse_pilot_scalar(value):
    """Parse the deliberately simple scalar subset used by benchmarks/cases.yaml."""
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        return [] if not inner else [item.strip() for item in inner.split(",")]
    if value.startswith("{") and value.endswith("}"):
        return json.loads(value)
    if value == "true":
        return True
    if value == "false":
        return False
    return value


def load_pilot_cases():
    """Load cases.yaml without PyYAML; the fixture intentionally uses a flat YAML subset."""
    cases = []
    current = None
    for raw_line in PILOT_CASES.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line == "cases:":
            continue
        if line.startswith("- case_id:"):
            if current is not None:
                cases.append(current)
            current = {"case_id": parse_pilot_scalar(line.split(":", 1)[1])}
            continue
        if current is None or ":" not in line:
            raise ValueError(f"Unsupported pilot fixture line: {raw_line}")
        key, value = line.split(":", 1)
        current[key.strip()] = parse_pilot_scalar(value)
    if current is not None:
        cases.append(current)
    allowed_fields = set(PILOT_FIELDS) | set(PILOT_OPTIONAL_FIELDS)
    if len(cases) != 14 or any(not set(PILOT_FIELDS).issubset(case) or not set(case).issubset(allowed_fields) for case in cases):
        missing = [set(PILOT_FIELDS) - set(case) for case in cases]
        raise ValueError(f"Expected 14 compatible pilot cases in {PILOT_CASES}; got {len(cases)} (missing: {missing})")
    case_ids = [case["case_id"] for case in cases]
    if len(set(case_ids)) != len(case_ids):
        raise ValueError("Pilot case IDs must be unique")
    return cases


def materialize_pilot_projects(path):
    """Create text-only pilot projects using only the standard library."""
    cases = load_pilot_cases()
    path.mkdir(parents=True, exist_ok=True)
    manifest = path / "manifest.json"
    existing = load_json(manifest) if manifest.exists() else None
    expected_ids = [case["case_id"] for case in cases]
    if existing and existing.get("case_ids") == expected_ids:
        projects = [path / case_id for case_id in expected_ids]
        if all((project / "prompt.txt").exists() and (project / "context.yaml").exists() for project in projects):
            return projects, expected_ids
    for case in cases:
        case_id = case["case_id"]
        project = path / case_id
        project.mkdir(parents=True, exist_ok=True)
        normalized = {
            "id": case_id,
            "case_id": case_id,
            "scenario": case["scenario"],
            "locale": case["locale"],
            "title": case["title"],
            "context": case["context"],
            "audience": case["audience"],
            "surface": case["surface"],
            "behavior": case["behavior"],
            "prompt": case["prompt"],
            "constraints": case["expected_constraints"],
            "expected_constraints": case["expected_constraints"],
            "findings": case["expected_findings"],
            "expected_findings": case["expected_findings"],
            "positive_control": case["positive_control"],
            "composition": case["composition"],
            "copy_only": case.get("copy_only", bool(case["composition"])),
            "visible_sections": case.get("visible_sections", []),
            "conditions": case["conditions"],
            "rubric_applicability": case["rubric_applicability"],
            "invariants": case.get("invariants", []),
        }
        (project / "context.yaml").write_text(json.dumps(normalized, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        (project / "copy.txt").write_text("\n", encoding="utf-8")
        (project / "prompt.txt").write_text(case["prompt"] + "\n", encoding="utf-8")
        (project / "expected.yaml").write_text(json.dumps({
            "case_id": case_id,
            "expected_constraints": case["expected_constraints"],
            "findings": case["expected_findings"],
            "positive_control": case["positive_control"],
            "composition": case["composition"],
            "copy_only": case.get("copy_only", bool(case["composition"])),
            "visible_sections": case.get("visible_sections", []),
            "conditions": case["conditions"],
            "rubric_applicability": case["rubric_applicability"],
            "invariants": case.get("invariants", []),
        }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    atomic_write(manifest, {"source": str(PILOT_CASES), "case_ids": expected_ids})
    return [path / case_id for case_id in expected_ids], expected_ids


def select_cases(scope, projects_dir, *, basic_only, fire_tests, fire_tests_only):
    """Select portable fixtures by default; local repositories require opt-in."""
    if scope == "pilot":
        raise ValueError("pilot cases are materialized separately")
    basic = [] if fire_tests_only else [(path.name, path, False) for path in ensure_basic_projects(pathlib.Path(projects_dir))]
    # --fire-tests-only remains an explicit request for the legacy fire scope.
    fire = [(name, pathlib.Path(path), True) for name, path in FIRE_TESTS.items() if pathlib.Path(path).is_dir()] if (fire_tests or fire_tests_only) and not basic_only else []
    return basic + fire


def select_pilot_cases(projects, case_ids, requested_ids=None, limit=None):
    """Select pilot cases without silently rerunning or duplicating scenarios."""
    if requested_ids:
        if not 1 <= len(requested_ids) <= 4:
            raise SystemExit("--case-id requires between one and four pilot case IDs")
        if len(set(requested_ids)) != len(requested_ids):
            raise SystemExit("--case-id values must be unique")
        known = set(case_ids)
        unknown = [case_id for case_id in requested_ids if case_id not in known]
        if unknown:
            raise SystemExit("Unknown pilot case ID(s): " + ", ".join(unknown))
        by_id = dict(zip(case_ids, projects))
        return [(case_id, by_id[case_id], False) for case_id in requested_ids]
    selected = [(case_id, project, False) for case_id, project in zip(case_ids, projects)]
    return selected[:limit] if limit is not None else selected


def validate_single_run_args(args):
    """Reject every matrix option that could exceed one balanced pilot run."""
    if not args.single_run:
        return
    invalid = []
    if args.scope != "pilot":
        invalid.append("--scope pilot")
    if args.condition != ["balanced"]:
        invalid.append("--condition balanced")
    if args.repetitions != 1:
        invalid.append("--repetitions 1")
    if args.limit != 1:
        invalid.append("--limit 1")
    if args.basic_only:
        invalid.append("without --basic-only")
    if args.fire_tests or args.fire_tests_only:
        invalid.append("without fire-test options")
    if args.resume or args.checkpoint:
        invalid.append("without --resume/--checkpoint")
    if invalid:
        raise SystemExit("--single-run requires exactly one balanced pilot invocation (" + ", ".join(invalid) + ")")


def revision(path):
    try:
        return subprocess.run(["git", "-C", str(path), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unversioned"


def project_context_hash(project):
    parts = []
    for name in ("context.yaml", "copy.txt", "prompt.txt", "expected.yaml"):
        path = project / name
        if path.exists():
            parts.append(name + "\0" + path.read_text(encoding="utf-8"))
    return digest("\n".join(parts))


def empty_telemetry():
    return {key: None for key in TELEMETRY_FIELDS} | {"observed": False}


def fixture_context(project):
    path = project / "context.yaml"
    if not path.exists():
        return {}, ""
    raw = path.read_text(encoding="utf-8")
    try:
        return load_json(path), raw
    except json.JSONDecodeError:
        return {}, raw


def locale_directive(context):
    locale = str(context.get("locale", "")).lower()
    if locale.startswith("es"):
        return (
            "\nLocale directive: Write the human summary and every prose value in Spanish for the requested/inferred "
            "locale (es-419); never English. Keep fixed schema keys and route identifiers in English."
        )
    if locale.startswith("en"):
        return (
            "\nLocale directive: Write the human summary and every prose value in English for the requested/inferred "
            "locale. Keep fixed schema keys and route identifiers in English."
        )
    return ""


def copy_only_contract(context):
    """Return the shared visible-copy format used by baseline and balanced compose runs."""
    sections = context.get("visible_sections", [])
    headings = ", ".join(sections) if sections else "the requested visible sections"
    invariants = context.get("invariants", [])
    constraints = "\n".join(f"- {item}" for item in invariants) or "- Preserve every declared behavior and claim boundary."
    return (
        "\n--- visible copy contract ---\n"
        f"Return only visible copy under these Markdown H2 headings, in this order: {headings}. "
        "Do not add a summary, diagnosis, rationale, findings, assumptions, project context, execution profile, telemetry, or JSON/YAML object. "
        "Treat these declared invariants as correctness constraints, not headings or prose to repeat:\n"
        + constraints
        + "\n--- end visible copy contract ---\n"
    )


def validate_copy_only_output(output, context):
    """Validate declared visible sections without judging literal copy quality."""
    errors = []
    lowered = output.casefold()
    for section in context.get("visible_sections", []):
        heading = f"## {section}".casefold()
        if heading not in lowered:
            errors.append(f"missing visible section heading: {section}")
    for forbidden in ("diagnosis", "rationale", "project_context", "execution_profile", "telemetry"):
        if f"## {forbidden}" in lowered or f'"{forbidden}"' in lowered:
            errors.append(f"visible copy must not include {forbidden}")
    return errors


def composition_output_diagnostics(output, context):
    """Validate shared copy-only format for every composition condition."""
    return validate_copy_only_output(output, context)


def prompt_details(project, condition, fire=False):
    context_data = {}
    if fire:
        prompt = (
            "Audit one bounded user-facing language flow in this repository. Read only README.md, "
            "AGENTS.md when present, locale files, and the smallest named files needed to answer. "
            "Do not edit files. Report concrete current copy, problems, recommended replacements, "
            "locale, tone, rationale, confidence, and contradictions with code."
        )
    else:
        prompt = (project / "prompt.txt").read_text(encoding="utf-8")
        context_data, context = fixture_context(project)
        existing_copy = (project / "copy.txt").read_text(encoding="utf-8") if (project / "copy.txt").exists() else ""
        prompt += "\n\nFixture context (authoritative for this case):\n" + context
        if existing_copy:
            prompt += "\n\nExisting copy to review or preserve when requested:\n" + existing_copy
    shared = locale_directive(context_data)
    if context_data.get("composition"):
        shared += copy_only_contract(context_data)
    if condition == "baseline":
        return prompt + shared + "\nDo not load or use adaptive-product-language. Follow the visible copy contract when supplied.", ()
    instructions = (
        prompt
        + shared
        + f"\nUse adaptive-product-language. Execution profile: {condition}."
        + "\nAll required reference content for this benchmark is already included below. Do not search the filesystem, use shell, file-search, web, or other tools, or try to discover external skills. Answer only from the fixture context and these inline instructions."
    )
    if context_data.get("composition"):
        contextual_adaptation = (SKILL / "references" / "contextual-adaptation.md").read_text(encoding="utf-8")
        language_quality = (SKILL / "references" / "language-quality.md").read_text(encoding="utf-8")
        return (
            instructions
            + "\n--- references/contextual-adaptation.md ---\n" + contextual_adaptation
            + "\n--- references/language-quality.md ---\n" + language_quality
            + "\n--- end compose references ---\nFollow the visible copy contract.",
            COMPOSE_REFERENCES,
        )
    skill_instructions = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    injected = instructions + "\n\n--- adaptive-product-language/SKILL.md ---\n" + skill_instructions + "\n--- end skill instructions ---\n"
    decision_system = (SKILL / "references" / "decision-system.md").read_text(encoding="utf-8")
    return (
        injected
        + "\n--- adaptive-product-language/references/decision-system.md (canonical contract) ---\n"
        + decision_system
        + "\n--- end canonical contract ---\n"
        + "Return the skill's structured contract.",
        ("SKILL.md", "references/decision-system.md"),
    )

def prompt_for(project, condition, fire=False):
    return prompt_details(project, condition, fire)[0]


def apply_runner_telemetry(telemetry, prompt, injected_references):
    """Preserve runner-owned prompt observations from event payloads."""
    telemetry["context_bytes"] = len(prompt.encode("utf-8"))
    telemetry["references"] = len(injected_references)
    return telemetry


def parse_events(text):
    telemetry = empty_telemetry()
    final = ""
    tool_call_ids = set()

    def copy_observed(source):
        if not isinstance(source, dict):
            return
        for key in TELEMETRY_FIELDS:
            if key in source:
                telemetry[key] = source[key]

    for line in text.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        copy_observed(event)
        copy_observed(event.get("telemetry"))
        if event.get("type") == "item.completed":
            item = event.get("item", {})
            copy_observed(item)
            copy_observed(item.get("telemetry"))
            if item.get("type") == "agent_message":
                final = item.get("text", final)
            if item.get("type") in TOOL_CALL_ITEM_TYPES:
                tool_call_ids.add(str(item.get("id") or event.get("item_id") or f"completed:{len(tool_call_ids)}"))
        if event.get("type") in {"tool_call", "tool_call.completed", "tool_call.started", "function_call", "function_call.completed"}:
            tool_call_ids.add(str(event.get("id") or event.get("item_id") or f"event:{len(tool_call_ids)}"))
        if event.get("type") == "turn.completed":
            usage = event.get("usage", {})
            telemetry["input_tokens"] = usage.get("input_tokens")
            telemetry["cached_input_tokens"] = usage.get("cached_input_tokens") or usage.get("input_tokens_details", {}).get("cached_tokens")
            telemetry["output_tokens"] = usage.get("output_tokens")
            telemetry["reasoning_output_tokens"] = usage.get("reasoning_output_tokens") or usage.get("output_tokens_details", {}).get("reasoning_tokens")
            telemetry["elapsed_ms"] = event.get("elapsed_ms") or event.get("duration_ms")
    telemetry["tool_calls"] = len(tool_call_ids) or None
    telemetry["observed"] = any(value is not None for key, value in telemetry.items() if key != "observed")
    return final, telemetry


def expected_for(project):
    path = project / "expected.yaml"
    if not path.exists():
        return []
    try:
        value = load_json(path)
    except (OSError, json.JSONDecodeError):
        return []
    return value.get("findings", value.get("expected_findings", []))


def run_one(project, case_id, condition, pair_id, replicate_id, condition_order, out_dir, model, fire=False, dry_run=False):
    out_dir.mkdir(parents=True, exist_ok=True)
    # Stable identity makes retries overwrite the same result instead of
    # creating duplicate records in aggregate/evaluation reports.
    run_id = f"{case_id}-{condition}-rep-{replicate_id:02d}"
    prompt, injected_references = prompt_details(project, condition, fire)
    result_path = out_dir / f"{run_id}.json"
    events_path = out_dir / "raw" / f"{run_id}.jsonl"
    events_path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "benchmark_protocol_version": BENCHMARK_PROTOCOL_VERSION,
        "case_id": case_id, "condition": condition, "pair_id": pair_id, "replicate_id": replicate_id, "run_id": run_id,
        "model": {"name": model, "provider": "codex", "version": None, "reasoning_effort": None, "service_tier": None, "temperature": None, "seed": None},
        "prompt_context": {"prompt_hash": digest(prompt), "context_hash": project_context_hash(project), "condition_order": list(condition_order)},
        "output": "", "expected_findings": expected_for(project) if not fire else [], "expected_findings_found": [], "coverage": None,
        "quality_scores": {key: None for key in QUALITY_DIMENSIONS},
        "rubric_applicability": load_json(project / "context.yaml").get("rubric_applicability", {key: True for key in QUALITY_DIMENSIONS}) if not fire else {key: True for key in QUALITY_DIMENSIONS},
        "telemetry": empty_telemetry(),
        "evaluator": {"evaluator_id": "", "blind": True, "scored_at": "", "notes": "", "completeness": None, "range_valid": None, "agreement": None},
        "diagnostics": [],
        "project_environment": {"id": case_id if fire else "standalone", "revision": revision(project), "scope": "bounded read-only fire test" if fire else "portable fixture"},
    }
    # These are runner-owned prompt observations, not API token estimates.
    # They are available even when Codex is not invoked or event telemetry is absent.
    record["telemetry"]["context_bytes"] = len(prompt.encode("utf-8"))
    record["telemetry"]["references"] = len(injected_references)
    if dry_run:
        record["telemetry"]["profile"] = condition
        record["telemetry"]["stop_reason"] = "dry_run"
        record["telemetry"]["observed"] = True
        record["evaluator"]["notes"] = "dry-run; Codex was not invoked"
        record["diagnostics"].append("quality unobserved; blind evaluation required")
        atomic_write(result_path, record)
        return "DRY", result_path

    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".txt", delete=False) as handle:
        handle.write(prompt)
        prompt_path = pathlib.Path(handle.name)
    # Benchmark runs must not inherit the host's Codex configuration, MCP
    # connections, hooks, or unrelated session context. Those inputs dwarf the
    # fixture prompt and make token/latency comparisons invalid.
    command = [
        "codex", "exec", "--ephemeral", "--json", "--ignore-user-config",
        "--ignore-rules", "--skip-git-repo-check", "--sandbox", "read-only",
        "-C", str(project), "-o", str(out_dir / "raw" / f"{run_id}.last.txt"),
    ]
    completed = None
    started = time.monotonic()
    try:
        with events_path.open("w", encoding="utf-8") as events, prompt_path.open(encoding="utf-8") as prompt_file:
            completed = subprocess.run(command, stdin=prompt_file, stdout=events, stderr=subprocess.STDOUT, text=True)
        events_text = events_path.read_text(encoding="utf-8", errors="replace")
        output, telemetry = parse_events(events_text)
        apply_runner_telemetry(telemetry, prompt, injected_references)
        telemetry["elapsed_ms"] = telemetry["elapsed_ms"] or round((time.monotonic() - started) * 1000)
        telemetry["profile"] = condition
        if completed is not None and completed.returncode == 0:
            telemetry["stop_reason"] = telemetry["stop_reason"] or "completed"
        elif completed is not None and completed.returncode < 0:
            telemetry["stop_reason"] = "interrupted"
            telemetry["interruptions"] = telemetry["interruptions"] if telemetry["interruptions"] is not None else 1
        elif completed is not None:
            telemetry["stop_reason"] = f"exit_code_{completed.returncode}"
        telemetry["observed"] = True
        fallback_path = out_dir / "raw" / f"{run_id}.last.txt"
        fallback = fallback_path.read_text(encoding="utf-8", errors="replace") if fallback_path.exists() else events_text
        record["output"] = output or fallback
        record["telemetry"] = telemetry
        if not fire and load_json(project / "context.yaml").get("composition") and record["output"]:
            record["diagnostics"].extend(composition_output_diagnostics(record["output"], load_json(project / "context.yaml")))
        record["evaluator"]["notes"] = "Codex exit code " + str(completed.returncode if completed else "unknown")
        if completed is None or completed.returncode:
            record["evaluator"]["notes"] += "; execution failed or was interrupted"
            record["diagnostics"].append("execution failed or was interrupted")
    except KeyboardInterrupt:
        events_text = events_path.read_text(encoding="utf-8", errors="replace") if events_path.exists() else ""
        record["output"], telemetry = parse_events(events_text)
        apply_runner_telemetry(telemetry, prompt, injected_references)
        telemetry["elapsed_ms"] = telemetry["elapsed_ms"] or round((time.monotonic() - started) * 1000)
        telemetry["profile"] = condition
        telemetry["stop_reason"] = "interrupted"
        telemetry["interruptions"] = telemetry["interruptions"] if telemetry["interruptions"] is not None else 1
        telemetry["observed"] = True
        record["telemetry"] = telemetry
        record["evaluator"]["notes"] = "execution interrupted"
        record["diagnostics"].append("execution interrupted")
    except (OSError, subprocess.SubprocessError) as error:
        record["evaluator"]["notes"] = f"runner error: {type(error).__name__}: {error}"
        record["output"] = events_path.read_text(encoding="utf-8", errors="replace") if events_path.exists() else ""
        record["telemetry"]["elapsed_ms"] = round((time.monotonic() - started) * 1000)
        record["telemetry"]["profile"] = condition
        record["telemetry"]["stop_reason"] = "runner_error"
        record["telemetry"]["observed"] = True
        record["diagnostics"].append("runner error")
    finally:
        prompt_path.unlink(missing_ok=True)
    atomic_write(result_path, record)
    return ("OK" if completed is not None and completed.returncode == 0 else "FAIL"), result_path


def write_report(path, records, checkpoint, *, single_run=False):
    observed = {key: sum(record.get("telemetry", {}).get(key) is not None for record in records) for key in TELEMETRY_FIELDS}
    lines = ["# Codex benchmark execution report", "", "This runner records observed execution telemetry only. Quality is unobserved until blind evaluation.", "", f"- Records: {len(records)}", f"- Checkpoint: `{checkpoint}`", "- Observed telemetry fields:"]
    lines.extend(f"  - {key}: {count}/{len(records)} records" for key, count in observed.items())
    if single_run:
        protocol = records[0].get("benchmark_protocol_version", "unknown") if records else "unknown"
        telemetry = records[0].get("telemetry", {}) if records else {}
        lines.extend([
            "", "## Single-run guard", "", "- Invocation count: 1",
            f"- Protocol: `{protocol}`",
            "- Objective validation: execution captured; quality scores remain unassigned until blind evaluation.",
            f"- Telemetry: `{json.dumps(telemetry, sort_keys=True)}`",
        ])
    lines.extend(["", "Use `evaluate_results.py create` and `report` for blind quality scoring; do not interpret missing values as zero."])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default=str(HERE / "results" / "codex"))
    parser.add_argument("--projects-dir", default=str(DEFAULT_PROJECTS))
    parser.add_argument("--scope", choices=("pilot", "basic"), default="basic", help="pilot uses the 14 cases from cases.yaml; basic uses the 30 generated fixtures")
    parser.add_argument("--basic-only", action="store_true")
    parser.add_argument("--fire-tests", action="store_true", help="include opt-in read-only local fire repositories alongside portable fixtures")
    parser.add_argument("--fire-tests-only", action="store_true", help="run only read-only local fire repositories (implies fire-test opt-in)")
    parser.add_argument("--limit", type=int, help="limit cases, not repetitions or conditions")
    parser.add_argument("--case-id", dest="case_ids", action="append", help="select one to four pilot case IDs; repeat for each ID")
    parser.add_argument("--repetitions", type=int, default=1)
    parser.add_argument("--condition", choices=CONDITIONS, action="append")
    parser.add_argument("--model", default="codex-default")
    parser.add_argument("--seed", default="apl-pilot")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--confirm", action="store_true", help="required for more than 8 executions")
    parser.add_argument("--checkpoint")
    parser.add_argument("--resume")
    parser.add_argument("--report")
    parser.add_argument("--single-run", action="store_true", help="allow exactly one balanced pilot invocation for maintainer validation")
    args = parser.parse_args()
    validate_single_run_args(args)
    if args.basic_only and (args.fire_tests or args.fire_tests_only):
        parser.error("--basic-only cannot be combined with fire-test options")
    if args.scope == "pilot" and args.fire_tests_only:
        parser.error("--fire-tests-only cannot be combined with --scope pilot")
    if args.case_ids and args.scope != "pilot":
        parser.error("--case-id can only be used with --scope pilot")
    if args.case_ids and args.limit is not None:
        parser.error("--case-id cannot be combined with --limit")
    if args.repetitions < 1:
        parser.error("--repetitions must be at least 1")

    output = pathlib.Path(args.output_dir)
    checkpoint = pathlib.Path(args.resume or args.checkpoint or (output / "checkpoint.json"))
    saved = load_json(pathlib.Path(args.resume)) if args.resume else None
    if saved:
        require_current_protocol(saved, checkpoint)
        output = pathlib.Path(saved["output_dir"])
        conditions = tuple(saved["conditions"])
        repetitions = saved["repetitions"]
        seed = saved["seed"]
        scope = saved.get("scope", "basic")
        materialized_cases = [pathlib.Path(item) for item in saved.get("materialized_cases", [])]
        cases = [(item["case_id"], pathlib.Path(item["path"]), item["fire"]) for item in saved["cases"]]
        missing = [str(path) for path in materialized_cases if not path.exists()]
        if missing:
            raise SystemExit("Cannot resume: materialized benchmark cases are missing: " + ", ".join(missing))
    else:
        conditions = tuple(args.condition or CONDITIONS)
        repetitions = args.repetitions
        seed = args.seed
        scope = args.scope
        if scope == "pilot":
            pilot_root = output / "materialized-pilot"
            pilot_projects, pilot_ids = materialize_pilot_projects(pilot_root)
            materialized_cases = pilot_projects
            cases = select_pilot_cases(pilot_projects, pilot_ids, args.case_ids, args.limit)
        else:
            materialized_cases = []
            cases = select_cases(scope, args.projects_dir, basic_only=args.basic_only, fire_tests=args.fire_tests, fire_tests_only=args.fire_tests_only)
        if args.limit and scope != "pilot":
            cases = cases[:args.limit]
    if not cases:
        raise SystemExit("No benchmark cases found")
    if args.single_run and cases[0][0] not in {SINGLE_RUN_CASE, "enus_login_screen"}:
        raise SystemExit("--single-run requires the es419_cta or enus_login_screen pilot fixture")

    total = len(cases) * repetitions * len(conditions)
    if total > 8 and not args.confirm and not args.dry_run and not args.resume:
        raise SystemExit(f"Refusing {total} executions. Re-run with --confirm (or --dry-run first).")
    report = pathlib.Path(args.report or (output / "report.md"))
    state = saved or {
        "version": 3, "benchmark_protocol_version": BENCHMARK_PROTOCOL_VERSION,
        "output_dir": str(output), "model": args.model, "scope": scope, "conditions": list(conditions),
        "repetitions": repetitions, "seed": seed,
        "materialized_cases": [str(project) for project in materialized_cases],
        "cases": [{"case_id": case_id, "path": str(project), "fire": is_fire} for case_id, project, is_fire in cases],
        "runs": {},
    }
    statuses = []
    for case_id, project, is_fire in cases:
        for replicate_id in range(1, repetitions + 1):
            pair_id = f"{case_id}-rep-{replicate_id:02d}"
            ordered = list(conditions)
            random.Random(f"{seed}:{pair_id}").shuffle(ordered)
            for condition in ordered:
                key = f"{pair_id}:{condition}"
                prior = state["runs"].get(key)
                # Completed runs are immutable checkpoint work. Failed or
                # interrupted runs must be retried after quota/tool recovery.
                if prior and prior.get("status") == "completed" and pathlib.Path(prior.get("result_path", "")).exists():
                    print(f"SKIP {case_id} rep {replicate_id} {condition} (checkpoint)", flush=True)
                    continue
                state["runs"][key] = {"key": key, "status": "running", "case_id": case_id, "condition": condition, "pair_id": pair_id, "replicate_id": replicate_id}
                atomic_write(checkpoint, state)
                status, result_path = run_one(project, case_id, condition, pair_id, replicate_id, ordered, output, state["model"], is_fire, args.dry_run)
                statuses.append(status)
                state["runs"][key].update({"status": "completed" if status in {"OK", "DRY"} else "failed", "result_path": str(result_path)})
                atomic_write(checkpoint, state)
                print(f"{status:4} {case_id} rep {replicate_id} {condition} -> {result_path}", flush=True)

    records = []
    for path in sorted(output.glob("*.json")):
        if path.name == checkpoint.name:
            continue
        try:
            records.append(load_json(path))
        except json.JSONDecodeError:
            pass
    write_report(report, records, checkpoint, single_run=args.single_run)
    print(f"completed {len(statuses)} runs: {statuses.count('OK')} ok, {statuses.count('FAIL')} failed, {statuses.count('DRY')} dry-run")
    print(f"checkpoint: {checkpoint}")
    print(f"report: {report}")
    print(f"aggregate: python3 {HERE / 'aggregate.py'} --results-dir {output} --json")


if __name__ == "__main__":
    main()
