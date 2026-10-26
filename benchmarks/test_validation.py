#!/usr/bin/env python3
"""Standard-library contract tests for the adaptive benchmark fixtures."""
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import validate_basic_environments  # noqa: E402
import evaluate_results  # noqa: E402
import aggregate  # noqa: E402
import run_codex_benchmark  # noqa: E402
from benchmark_protocol import BENCHMARK_PROTOCOL_VERSION  # noqa: E402


class FixtureContractTests(unittest.TestCase):
    def setUp(self):
        self.rows = json.loads((HERE / "basic-environments.yaml").read_text(encoding="utf-8"))

    def test_manifest_covers_all_scenarios_and_required_context(self):
        self.assertEqual(validate_basic_environments.validate_manifest(self.rows), [])
        self.assertEqual({row["scenario"] for row in self.rows}, validate_basic_environments.SCENARIOS)
        for row in self.rows:
            for key in ("context", "audience", "surface", "locale", "risk", "behavior", "constraints", "invariants", "findings"):
                self.assertIn(key, row, row["id"])

    def test_manifest_has_compositions_and_positive_controls(self):
        self.assertGreaterEqual(sum(bool(row["composition"]) for row in self.rows), 8)
        controls = [row for row in self.rows if row["positive_control"]]
        self.assertGreaterEqual(len(controls), 3)
        self.assertTrue(all(row["findings"] == [] for row in controls))

    def test_generator_and_validator_round_trip(self):
        with tempfile.TemporaryDirectory() as directory:
            subprocess.run([sys.executable, str(HERE / "generate_basic_projects.py"), "--output-dir", directory, "--clean"], check=True, stdout=subprocess.PIPE, text=True)
            result = subprocess.run([sys.executable, str(HERE / "validate_basic_environments.py"), "--projects", directory], check=False, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("30 records", result.stdout)


    def test_blind_context_redacts_answer_keys(self):
        with tempfile.TemporaryDirectory() as directory:
            project = pathlib.Path(directory) / "basic-01"
            project.mkdir()
            (project / "context.yaml").write_text(json.dumps({
                "id": "basic-01", "case_id": "basic-01", "context": "fixture", "findings": ["clarity"],
                "expected_findings": ["clarity"], "positive_control": False, "conditions": ["baseline"],
                "composition": {"kind": "form"}, "locale": "en-US", "behavior": "save",
            }), encoding="utf-8")
            (project / "copy.txt").write_text("Continue", encoding="utf-8")
            (project / "prompt.txt").write_text("Review the CTA", encoding="utf-8")
            context = evaluate_results.fixture_context("basic-01", directory)
            self.assertNotIn("id", context["context.yaml"])
            self.assertNotIn("findings", context["context.yaml"])
            self.assertNotIn("positive_control", context["context.yaml"])
            self.assertNotIn("expected_findings", context["context.yaml"])
            self.assertNotIn("conditions", context["context.yaml"])
            self.assertNotIn("composition", context["context.yaml"])
            self.assertNotIn("case_id", context["context.yaml"])
            self.assertNotIn("expected.yaml", context)

    def test_cases_file_declares_fourteen_pilot_cases(self):
        text = (HERE / "cases.yaml").read_text(encoding="utf-8")
        self.assertEqual(text.count("- case_id:"), 14)
        self.assertEqual(text.count("conditions: [baseline, light, balanced, performance]"), 14)

    def test_contextual_landing_fixtures_have_copy_only_context_and_invariants(self):
        cases = {case["case_id"]: case for case in run_codex_benchmark.load_pilot_cases()}
        for case_id, locale, sections in (
            ("es419_contextual_phone_landing", "es-419", ("Hero", "Beneficios", "Confianza", "Catálogo", "FAQ", "CTA")),
            ("enUS_contextual_saas_landing", "en-US", ("Hero", "Benefits", "Trust", "Features", "FAQ", "CTA")),
        ):
            fixture = cases[case_id]
            self.assertEqual(fixture["locale"], locale)
            self.assertTrue(fixture["composition"])
            self.assertTrue(fixture["copy_only"])
            self.assertIn("solo" if locale.startswith("es") else "only", fixture["prompt"])
            for section in sections:
                self.assertIn(section, fixture["surface"] + fixture["prompt"] + " ".join(fixture["visible_sections"]))
            self.assertGreaterEqual(len(fixture["invariants"]), 6)
            self.assertTrue(all(fixture["rubric_applicability"][key] for key in run_codex_benchmark.QUALITY_DIMENSIONS))
        self.assertIn("no inventa precios descuentos inventario ni entregas", cases["es419_contextual_phone_landing"]["invariants"])
        self.assertIn("does not invent integrations uptime security certification implementation time pricing free trial or compliance", cases["enUS_contextual_saas_landing"]["invariants"])

    def test_evaluator_rejects_incomplete_and_out_of_range_scores(self):
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "scores.jsonl"
            incomplete = {"blind_id": "sample-1", "evaluator_id": "evaluator-a", "evidence": "observed"}
            path.write_text(json.dumps(incomplete) + "\n", encoding="utf-8")
            with self.assertRaises(SystemExit):
                evaluate_results.parse_scores([path], {"sample-1"})
            invalid = {"blind_id": "sample-1", "evaluator_id": "evaluator-a", "applicable_dimensions": list(evaluate_results.DIMENSIONS), "evidence": "observed", "critical_regression": False}
            invalid.update({dimension: 5 for dimension in evaluate_results.DIMENSIONS})
            path.write_text(json.dumps(invalid) + "\n", encoding="utf-8")
            with self.assertRaises(SystemExit):
                evaluate_results.parse_scores([path], {"sample-1"})

    def test_aggregate_includes_optional_telemetry_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            result = {
                "benchmark_protocol_version": BENCHMARK_PROTOCOL_VERSION,
                "case_id": "case-1", "condition": "balanced", "run_id": "run-1",
                "pair_id": "case-1-rep-01", "model": {"provider": "codex"}, "output": "",
                "quality_scores": {dimension: None for dimension in aggregate.QUALITY_KEYS},
                "expected_findings_found": [], "telemetry": {
                    key: None for key in aggregate.TELEMETRY_KEYS
                }, "evaluator": {}, "project_environment": {
                    "id": "standalone", "revision": "unversioned", "scope": "fixture"
                },
            }
            result["telemetry"].update({"context_bytes": 12, "profile": "balanced", "stop_reason": "completed"})
            (pathlib.Path(directory) / "run-1.json").write_text(json.dumps(result), encoding="utf-8")
            completed = subprocess.run([sys.executable, str(HERE / "aggregate.py"), "--results-dir", directory, "--json"], check=True, capture_output=True, text=True)
            report = json.loads(completed.stdout)
            self.assertIn("context_bytes", report["efficiency"]["fields"])
            self.assertEqual(report["summaries"][0]["telemetry_mean"]["context_bytes"], 12)
            self.assertEqual(report["summaries"][0]["telemetry_values"]["profile"], ["balanced"])

    def test_fire_repositories_are_opt_in_but_fire_only_remains_available(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            basic = root / "basic-01"
            fire = root / "fire-project"
            basic.mkdir()
            fire.mkdir()
            with mock.patch.object(run_codex_benchmark, "ensure_basic_projects", return_value=[basic]), mock.patch.object(run_codex_benchmark, "FIRE_TESTS", {"fire": str(fire)}):
                default_cases = run_codex_benchmark.select_cases("basic", root, basic_only=False, fire_tests=False, fire_tests_only=False)
                opted_in_cases = run_codex_benchmark.select_cases("basic", root, basic_only=False, fire_tests=True, fire_tests_only=False)
                fire_only_cases = run_codex_benchmark.select_cases("basic", root, basic_only=False, fire_tests=False, fire_tests_only=True)
            self.assertEqual(default_cases, [("basic-01", basic, False)])
            self.assertEqual(opted_in_cases, [("basic-01", basic, False), ("fire", fire, True)])
            self.assertEqual(fire_only_cases, [("fire", fire, True)])

    def test_non_composition_prompt_embeds_the_canonical_decision_system(self):
        with tempfile.TemporaryDirectory() as directory:
            project = pathlib.Path(directory)
            (project / "prompt.txt").write_text("Review this", encoding="utf-8")
            (project / "context.yaml").write_text(json.dumps({"locale": "en-US", "composition": False}), encoding="utf-8")
            prompt = run_codex_benchmark.prompt_for(project, "balanced")
            canonical = (ROOT / "references" / "decision-system.md").read_text(encoding="utf-8")
            self.assertIn(canonical, prompt)
            self.assertIn("canonical contract", prompt)

    def test_prompt_adds_locale_directive_for_spanish_and_english_fixtures(self):
        with tempfile.TemporaryDirectory() as directory:
            project = pathlib.Path(directory)
            (project / "prompt.txt").write_text("Compose copy", encoding="utf-8")
            for locale, expected in (("es-419", "never English"), ("en-US", "in English")):
                (project / "context.yaml").write_text(json.dumps({"locale": locale, "composition": False}), encoding="utf-8")
                prompt = run_codex_benchmark.prompt_for(project, "balanced")
                self.assertIn("Locale directive", prompt)
                self.assertIn(expected, prompt)
                self.assertIn("schema keys and route identifiers in English", prompt)

    def test_balanced_landing_compose_loads_only_contextual_adaptation_and_language_quality(self):
        with tempfile.TemporaryDirectory() as directory:
            project = pathlib.Path(directory)
            (project / "prompt.txt").write_text("Compose copy", encoding="utf-8")
            context = {"locale": "en-US", "composition": True, "copy_only": True, "visible_sections": ["Hero", "Benefits"], "invariants": ["preserve declared claims"]}
            (project / "context.yaml").write_text(json.dumps(context), encoding="utf-8")
            prompt, references = run_codex_benchmark.prompt_details(project, "balanced")
            self.assertEqual(references, run_codex_benchmark.COMPOSE_REFERENCES)
            self.assertEqual(references, ("references/contextual-adaptation.md", "references/language-quality.md"))
            self.assertIn("references/contextual-adaptation.md", prompt)
            self.assertIn("references/language-quality.md", prompt)
            self.assertNotIn("references/component-rules.md", prompt)
            self.assertNotIn("references/decision-system.md", prompt)
            self.assertIn("visible copy contract", prompt)
            self.assertNotIn("exactly one object", prompt)

    def test_composition_prompt_forbids_tools_and_external_skill_discovery(self):
        with tempfile.TemporaryDirectory() as directory:
            project = pathlib.Path(directory)
            (project / "prompt.txt").write_text("Compose copy", encoding="utf-8")
            (project / "context.yaml").write_text(json.dumps({"locale": "en-US", "composition": True}), encoding="utf-8")
            prompt = run_codex_benchmark.prompt_for(project, "balanced")
            self.assertIn("All required reference content for this benchmark is already included", prompt)
            for forbidden in ("Do not search the filesystem", "shell", "file-search", "web", "external skills"):
                self.assertIn(forbidden, prompt)
            self.assertIn("Answer only from the fixture context and these inline instructions", prompt)

    def test_baseline_and_balanced_compose_share_visible_format_and_validate_sections(self):
        context = {"composition": True, "visible_sections": ["Hero", "Benefits"], "invariants": ["preserve claims"]}
        baseline = run_codex_benchmark.copy_only_contract(context)
        balanced = run_codex_benchmark.copy_only_contract(context)
        self.assertEqual(baseline, balanced)
        output = "## Hero\nSpecific copy\n\n## Benefits\nGrounded copy"
        self.assertEqual(run_codex_benchmark.composition_output_diagnostics(output, context), [])
        errors = run_codex_benchmark.composition_output_diagnostics("## Hero\nCopy\n\n## Diagnosis\nMetadata", context)
        self.assertIn("missing visible section heading: Benefits", errors)
        self.assertIn("visible copy must not include diagnosis", errors)

    def test_pilot_case_ids_accept_one_to_four_known_unique_cases(self):
        projects = [pathlib.Path(case_id) for case_id in ("one", "two", "three", "four", "five")]
        case_ids = [project.name for project in projects]
        selected = run_codex_benchmark.select_pilot_cases(projects, case_ids, ["one"])
        self.assertEqual([case_id for case_id, _, _ in selected], ["one"])
        selected = run_codex_benchmark.select_pilot_cases(projects, case_ids, ["five", "two", "four", "one"])
        self.assertEqual([case_id for case_id, _, _ in selected], ["five", "two", "four", "one"])
        with self.assertRaisesRegex(SystemExit, "between one and four"):
            run_codex_benchmark.select_pilot_cases(projects, case_ids, ["one", "two", "three", "four", "five"])
        with self.assertRaisesRegex(SystemExit, "unique"):
            run_codex_benchmark.select_pilot_cases(projects, case_ids, ["one", "one"])
        with self.assertRaisesRegex(SystemExit, "Unknown"):
            run_codex_benchmark.select_pilot_cases(projects, case_ids, ["missing"])

    def test_pilot_limit_remains_compatible_without_case_ids(self):
        projects = [pathlib.Path(case_id) for case_id in ("one", "two", "three", "four")]
        selected = run_codex_benchmark.select_pilot_cases(projects, [project.name for project in projects], limit=2)
        self.assertEqual([case_id for case_id, _, _ in selected], ["one", "two"])


    def test_runner_owned_context_and_reference_telemetry_are_always_populated(self):
        with tempfile.TemporaryDirectory() as directory:
            project = pathlib.Path(directory)
            output = project / "results"
            (project / "prompt.txt").write_text("Compose copy", encoding="utf-8")
            (project / "context.yaml").write_text(json.dumps({"locale": "es-419", "composition": True}), encoding="utf-8")
            (project / "expected.yaml").write_text(json.dumps({"findings": []}), encoding="utf-8")
            status, result_path = run_codex_benchmark.run_one(
                project, "case-1", "balanced", "case-1-rep-01", 1, ("balanced",), output,
                "codex-default", dry_run=True,
            )
            record = json.loads(result_path.read_text(encoding="utf-8"))
            self.assertEqual(status, "DRY")
            self.assertEqual(record["telemetry"]["context_bytes"], len(run_codex_benchmark.prompt_for(project, "balanced").encode("utf-8")))
            self.assertEqual(record["telemetry"]["references"], 2)
            self.assertIsInstance(record["telemetry"]["context_bytes"], int)
            self.assertIsInstance(record["telemetry"]["references"], int)

    def test_router_maps_intents_and_excludes_visual_only_requests(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        routing = (ROOT / "references" / "intent-routing.md").read_text(encoding="utf-8")
        module_map = (ROOT / "references" / "module-map.md").read_text(encoding="utf-8")
        for route in ("compose", "improve", "audit", "remediate", "localize", "context"):
            self.assertIn(f"`{route}`", skill + routing)
        self.assertIn("visual-only", skill + routing)
        self.assertIn("benchmark", module_map)
        self.assertIn("maintainer-only", module_map)
        self.assertNotIn("benchmarks/", skill)

    def test_output_tiers_preserve_formal_contract(self):
        decision = (ROOT / "references" / "decision-system.md").read_text(encoding="utf-8")
        profiles = (ROOT / "references" / "execution-profiles.md").read_text(encoding="utf-8")
        self.assertIn("## Output tiers", decision)
        self.assertIn("exactly the 14-key object", decision)
        self.assertIn("12-key finding schema", decision + profiles)
        self.assertIn("Normal compose returns visible copy only", profiles)

    def test_single_run_guard_requires_one_balanced_pilot(self):
        valid = SimpleNamespace(
            single_run=True, scope="pilot", condition=["balanced"], repetitions=1,
            limit=1, basic_only=False, fire_tests=False, fire_tests_only=False,
            dry_run=False, resume=None, checkpoint=None,
        )
        run_codex_benchmark.validate_single_run_args(valid)
        dry_run = SimpleNamespace(**vars(valid))
        dry_run.dry_run = True
        run_codex_benchmark.validate_single_run_args(dry_run)
        for field, value in (("condition", ["baseline"]), ("limit", 2), ("fire_tests", True)):
            invalid = SimpleNamespace(**vars(valid))
            setattr(invalid, field, value)
            with self.assertRaisesRegex(SystemExit, "--single-run"):
                run_codex_benchmark.validate_single_run_args(invalid)

    def test_aggregate_and_evaluator_reject_older_protocol_records(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            old_record = {
                "case_id": "case-1", "condition": "baseline", "run_id": "run-1",
                "model": {"provider": "codex"}, "output": "", "quality_scores": {},
                "expected_findings_found": [], "telemetry": {}, "evaluator": {},
            }
            result = root / "run-1.json"
            result.write_text(json.dumps(old_record), encoding="utf-8")
            aggregate_run = subprocess.run([sys.executable, str(HERE / "aggregate.py"), "--results-dir", str(root)], check=False, capture_output=True, text=True)
            self.assertNotEqual(aggregate_run.returncode, 0)
            self.assertIn("protocol", aggregate_run.stderr)
            with self.assertRaisesRegex(SystemExit, "protocol"):
                evaluate_results.create(type("Args", (), {"results_dir": root, "projects_dir": root, "output_dir": root / "evaluation", "seed": "test"})())

    def test_blind_packet_creation_keeps_answer_keys_private(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            results, projects, evaluation = root / "results", root / "projects", root / "evaluation"
            results.mkdir()
            project = projects / "case-1"
            project.mkdir(parents=True)
            (project / "context.yaml").write_text(json.dumps({
                "id": "case-1", "case_id": "case-1", "context": "safe", "expected_findings": ["answer"],
                "findings": ["answer"], "positive_control": True, "conditions": ["baseline"],
                "composition": {"kind": "form"}, "locale": "en-US", "behavior": "safe",
            }), encoding="utf-8")
            (project / "copy.txt").write_text("Copy", encoding="utf-8")
            (project / "prompt.txt").write_text("Review", encoding="utf-8")
            (results / "run-1.json").write_text(json.dumps({
                "benchmark_protocol_version": BENCHMARK_PROTOCOL_VERSION,
                "case_id": "case-1", "condition": "baseline", "run_id": "run-1", "output": "Safe output",
                "rubric_applicability": {dimension: True for dimension in evaluate_results.DIMENSIONS},
            }), encoding="utf-8")
            evaluate_results.create(type("Args", (), {"results_dir": results, "projects_dir": projects, "output_dir": evaluation, "seed": "test"})())
            packet = json.loads((evaluation / "blind-packets.jsonl").read_text(encoding="utf-8"))
            serialized = json.dumps(packet)
            for forbidden in ("expected_findings", "positive_control", "conditions", "composition", "case_id", '"id"'):
                self.assertNotIn(forbidden, serialized)
            private_map = json.loads((evaluation / "blind-map.json").read_text(encoding="utf-8"))
            self.assertEqual(private_map["mapping"][packet["blind_id"]]["case_id"], "case-1")

    def test_blind_packet_redacts_task_output_execution_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            results, projects, evaluation = root / "results", root / "projects", root / "evaluation"
            results.mkdir()
            project = projects / "case-1"
            project.mkdir(parents=True)
            (project / "context.yaml").write_text(json.dumps({
                "context": "safe", "locale": "en-US", "behavior": "safe",
            }), encoding="utf-8")
            output = """Summary: Keep the copy clear.
project_context:
  execution_profile: balanced
  profile: light
  condition: baseline
  provider: codex
  model: performance
  run_id: run-balanced-01
copy: Choose the balanced plan for your team.
quality_evidence: The CTA names the next step and preserves the user's context.
"""
            (results / "run-1.json").write_text(json.dumps({
                "benchmark_protocol_version": BENCHMARK_PROTOCOL_VERSION,
                "case_id": "case-1", "condition": "balanced", "run_id": "run-1", "output": output,
                "rubric_applicability": {dimension: True for dimension in evaluate_results.DIMENSIONS},
            }), encoding="utf-8")
            evaluate_results.create(type("Args", (), {"results_dir": results, "projects_dir": projects, "output_dir": evaluation, "seed": "test"})())

            packet = json.loads((evaluation / "blind-packets.jsonl").read_text(encoding="utf-8"))
            task_output = packet["task_output"]
            self.assertNotRegex(
                task_output,
                r"(?im)^\s*(?:execution[_ -]?profile|profile|condition|provider|model|run[_ -]?id)\s*:",
            )
            self.assertNotRegex(task_output, r"(?im)\b(?:baseline|light|balanced|performance)\b\s*$")
            self.assertNotRegex(task_output, r"run-balanced-01|codex")
            self.assertIn("Choose the balanced plan", task_output)
            self.assertIn("quality_evidence", task_output)

    def test_na_dimensions_are_excluded_and_critical_regression_blocks_win(self):
        dimensions = list(evaluate_results.DIMENSIONS)
        applicability = {"sample-baseline": tuple(dimensions[:-1]), "sample-profile": tuple(dimensions[:-1])}
        rows = []
        for blind_id, critical in (("sample-baseline", False), ("sample-profile", True)):
            row = {"blind_id": blind_id, "evaluator_id": "judge", "applicable_dimensions": dimensions[:-1], "critical_regression": critical, "evidence": "evidence"}
            row.update({dimension: 4 if blind_id == "sample-profile" else 3 for dimension in dimensions[:-1]})
            row[dimensions[-1]] = None
            rows.append(row)
        self.assertEqual(evaluate_results.row_quality(rows[0]), 3)
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            path = root / "scores.jsonl"
            path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")
            parsed, _ = evaluate_results.parse_scores([path], set(applicability), applicability)
            self.assertEqual(len(parsed), 2)
            mapping = {
                "sample-baseline": {"case_id": "case", "pair_id": "pair", "condition": "baseline", "source": "missing", "rubric_applicability": {dimension: dimension != dimensions[-1] for dimension in dimensions}},
                "sample-profile": {"case_id": "case", "pair_id": "pair", "condition": "balanced", "source": "missing", "rubric_applicability": {dimension: dimension != dimensions[-1] for dimension in dimensions}},
            }
            (root / "blind-map.json").write_text(json.dumps({"benchmark_protocol_version": BENCHMARK_PROTOCOL_VERSION, "mapping": mapping}), encoding="utf-8")
            subprocess.run([sys.executable, str(HERE / "evaluate_results.py"), "report", "--output-dir", str(root), "--scores", str(path)], check=True, capture_output=True, text=True)
            report = json.loads((root / "scored-report.json").read_text(encoding="utf-8"))
            self.assertEqual(report["paired_deltas"][0]["wins"], 0)
            self.assertTrue(report["paired_deltas"][0]["critical_regression"])

    def test_telemetry_retains_available_subtokens_and_tool_variants(self):
        events = "\n".join(json.dumps(item) for item in (
            {"type": "item.completed", "item": {"id": "call-1", "type": "function_call"}},
            {"type": "tool_call.completed", "id": "call-2"},
            {"type": "turn.completed", "usage": {"input_tokens": 10, "cached_input_tokens": 3, "output_tokens": 5, "reasoning_output_tokens": 2}},
        ))
        _, telemetry = run_codex_benchmark.parse_events(events)
        self.assertEqual(telemetry["cached_input_tokens"], 3)
        self.assertEqual(telemetry["reasoning_output_tokens"], 2)
        self.assertEqual(telemetry["tool_calls"], 2)

    def test_evaluator_separates_quality_efficiency_and_single_judge_agreement(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            results = root / "results"
            evaluation = root / "evaluation"
            results.mkdir()
            source = results / "run-1.json"
            source.write_text(json.dumps({
                "benchmark_protocol_version": BENCHMARK_PROTOCOL_VERSION,
                "case_id": "case-1", "condition": "baseline", "run_id": "run-1",
                "pair_id": "case-1-rep-01", "output": "output", "telemetry": {
                    "profile": "baseline", "context_bytes": 20
                }
            }), encoding="utf-8")
            mapping = {"sample-1": {"run_id": "run-1", "case_id": "case-1", "condition": "baseline", "pair_id": "case-1-rep-01", "source": str(source)}}
            evaluation.mkdir()
            (evaluation / "blind-map.json").write_text(json.dumps({"benchmark_protocol_version": BENCHMARK_PROTOCOL_VERSION, "mapping": mapping}), encoding="utf-8")
            scores = evaluation / "scores.jsonl"
            row = {"blind_id": "sample-1", "evaluator_id": "evaluator-a", "applicable_dimensions": list(evaluate_results.DIMENSIONS), "critical_regression": False, "evidence": "observed"}
            row.update({dimension: 3 for dimension in evaluate_results.DIMENSIONS})
            scores.write_text(json.dumps(row) + "\n", encoding="utf-8")
            subprocess.run([sys.executable, str(HERE / "evaluate_results.py"), "report", "--output-dir", str(evaluation), "--scores", str(scores)], check=True, capture_output=True, text=True)
            report = json.loads((evaluation / "scored-report.json").read_text(encoding="utf-8"))
            self.assertEqual(report["quality"]["score_rows"], 1)
            self.assertEqual(report["efficiency"]["telemetry_mean"]["context_bytes"], 20)
            self.assertIsNone(report["agreement"])


if __name__ == "__main__":
    unittest.main()
