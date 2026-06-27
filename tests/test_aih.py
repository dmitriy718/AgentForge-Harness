import json
import subprocess
import tempfile
import unittest
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AIH = ROOT / "scripts" / "aih"


def write_minimal_harness(root: Path) -> None:
    for directory in ("templates", "playbooks", "checklists", "swarm", "protocols", "rubrics", "packs", "runs"):
        (root / directory).mkdir(parents=True, exist_ok=True)

    for filename in (
        "INDEX.md",
        "HOW_TO_USE.md",
        "VERSION.md",
        "scripts/aih",
        "templates/00-universal-task-brief.md",
        "templates/01-codex-implementation.md",
        "templates/03-debug-diagnostic.md",
        "templates/04-code-review.md",
        "templates/07-agent-handoff.md",
        "protocols/production-readiness.md",
        "checklists/validation-gate.md",
    ):
        path = root / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# {filename}\n")

    for index in range(20):
        (root / "templates" / f"extra-{index:02d}.md").write_text(f"# Extra {index}\n")


def run_aih(*args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    process_env = os.environ.copy()
    if env:
        process_env.update(env)
    result = subprocess.run(
        [str(AIH), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        env=process_env,
        check=True,
    )
    return result


class AihOverlayTests(unittest.TestCase):
    def test_implementation_requests_route_to_codex(self) -> None:
        output = run_aih("prompt", "fix", "the", "harness", "that", "i", "am", "using", "to", "become", "more", "effective").stdout

        self.assertIn("- Mode: Implementation", output)
        self.assertIn("- Target: codex", output)
        self.assertIn("Do not stop at a plan", output)
        self.assertIn("Start with a high-level summary and current status.", output)

    def test_debug_requests_route_to_codex(self) -> None:
        output = run_aih("prompt", "debug", "docker", "compose", "login", "failure").stdout

        self.assertIn("- Mode: Debugging", output)
        self.assertIn("- Target: codex", output)
        self.assertIn("Rank likely causes by evidence.", output)

    def test_architecture_clause_is_not_duplicated(self) -> None:
        output = run_aih("ask", "choose between postgres queues and redis queues", "--mode", "architecture").stdout

        clause = "State the decision, why it wins, and what would change the decision."
        self.assertEqual(output.count(clause), 1)

    def test_plain_request_executes_through_codex_wrapper(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_aih(
                "fix",
                "the",
                "harness",
                env={"AIH_CODEX_BIN": "/bin/true", "AI_HARNESS_HOME": temp_dir},
            )

        self.assertIn("AIH executing with Codex.", result.stderr)
        self.assertIn("AIH run complete", result.stderr)
        self.assertIn("- Status: success (exit 0)", result.stderr)
        self.assertIn("- High-level summary:", result.stderr)

    def test_completion_summary_includes_captured_final_response(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            fake_codex = Path(temp_dir) / "fake-codex"
            fake_codex.write_text(
                "#!/usr/bin/env python3\n"
                "import pathlib, sys\n"
                "out = pathlib.Path(sys.argv[sys.argv.index('--output-last-message') + 1])\n"
                "out.write_text('Changed the harness.\\nValidation passed.\\n')\n"
            )
            fake_codex.chmod(0o755)

            result = run_aih(
                "fix",
                "the",
                "harness",
                env={"AIH_CODEX_BIN": str(fake_codex), "AI_HARNESS_HOME": temp_dir},
            )

        self.assertIn("Changed the harness.", result.stderr)
        self.assertIn("Validation passed.", result.stderr)

    def test_run_records_do_not_overwrite_and_redact_secret_like_values(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            request = "debug api_key=super-secret-token failure"
            first = Path(run_aih("run", request, env={"AI_HARNESS_HOME": temp_dir}).stdout.strip())
            second = Path(run_aih("run", request, env={"AI_HARNESS_HOME": temp_dir}).stdout.strip())

            self.assertNotEqual(first, second)
            self.assertTrue(first.exists())
            self.assertTrue(second.exists())
            self.assertEqual((first / "request.txt").read_text(), "debug [REDACTED] failure\n")
            self.assertIn("debug api_key=super-secret-token failure", (first / "prompt.md").read_text())

    def test_run_record_mode_warns_that_codex_work_was_not_executed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_aih("run", "fix", "the", "harness", env={"AI_HARNESS_HOME": temp_dir})

        self.assertIn("AIH run-record mode: no work was executed.", result.stderr)
        self.assertIn("To execute with Codex", result.stderr)

    def test_latest_run_json_returns_newest_run_record(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            first = Path(run_aih("run", "fix first issue", env={"AI_HARNESS_HOME": temp_dir}).stdout.strip())
            second = Path(run_aih("run", "fix second issue", env={"AI_HARNESS_HOME": temp_dir}).stdout.strip())
            payload = json.loads(run_aih("latest-run", "--json", env={"AI_HARNESS_HOME": temp_dir}).stdout)

        self.assertNotEqual(first, second)
        self.assertEqual(payload["run_dir"], str(second))
        self.assertEqual(payload["request"], "fix second issue")
        self.assertEqual(payload["metadata"]["target"], "codex")
        self.assertTrue(payload["prompt"].endswith("prompt.md"))

    def test_deep_requests_get_bounded_multi_pass_plan(self) -> None:
        request = (
            "fix i want you to first do a comprehensive codebase review and fix all findings "
            "then do additional 4 passes from different perspective amateur senior developer "
            "systems architect and ceo and continue until zero mistakes"
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            run_dir = Path(run_aih("run", request, env={"AI_HARNESS_HOME": temp_dir}).stdout.strip())

            prompt = (run_dir / "prompt.md").read_text()
            plan = (run_dir / "execution-plan.md").read_text()
            metadata = (run_dir / "metadata.txt").read_text()

        self.assertIn("## Deep Execution Plan", prompt)
        self.assertIn("Pass 2 - amateur perspective", plan)
        self.assertIn("Improvement 3 - implement one separate high-impact function", plan)
        self.assertIn("deep_execution=True", metadata)

    def test_deep_execution_announces_plan_before_codex(self) -> None:
        request = (
            "fix comprehensive codebase review all findings additional 4 passes "
            "amateur senior developer systems architect ceo zero mistakes"
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_aih(
                request,
                env={"AIH_CODEX_BIN": "/bin/true", "AI_HARNESS_HOME": temp_dir},
            )

        self.assertIn("AIH deep execution detected", result.stderr)
        self.assertIn("AIH execution plan:", result.stderr)

    def test_prompt_mode_warns_that_codex_work_was_not_executed(self) -> None:
        result = run_aih("prompt", "fix", "the", "harness")

        self.assertIn("AIH prompt-only mode: no work was executed.", result.stderr)
        self.assertIn("To execute with Codex", result.stderr)

    def test_prompt_mode_warns_when_deep_execution_would_apply(self) -> None:
        result = run_aih(
            "prompt",
            "fix comprehensive codebase review all findings additional 4 passes senior developer systems architect ceo zero mistakes",
        )

        self.assertIn("AIH prompt-only mode: no work was executed.", result.stderr)
        self.assertIn("AIH deep execution would be used if you run this request.", result.stderr)

    def test_prompt_mode_out_still_warns_when_codex_work_was_not_executed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            out = Path(temp_dir) / "prompt.md"
            result = run_aih("prompt", "fix", "the", "harness", "--out", str(out))

            self.assertEqual(result.stdout.strip(), str(out))
            self.assertIn("AIH prompt-only mode: no work was executed.", result.stderr)
            self.assertTrue(out.exists())

    def test_prompt_mode_save_still_warns_when_codex_work_was_not_executed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_aih(
                "prompt",
                "fix",
                "the",
                "harness",
                "--save",
                env={"AI_HARNESS_HOME": temp_dir},
            )

            self.assertIn("AIH prompt-only mode: no work was executed.", result.stderr)
            self.assertTrue(Path(result.stdout.strip()).exists())

    def test_new_run_records_do_not_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            templates = Path(temp_dir) / "templates"
            templates.mkdir()
            (templates / "00-universal-task-brief.md").write_text("# Brief\n")
            (templates / "07-agent-handoff.md").write_text("# Handoff\n")

            first = Path(run_aih("new-run", "same task", env={"AI_HARNESS_HOME": temp_dir}).stdout.strip())
            second = Path(run_aih("new-run", "same task", env={"AI_HARNESS_HOME": temp_dir}).stdout.strip())

            self.assertNotEqual(first, second)
            self.assertTrue((first / "task-brief.md").exists())
            self.assertTrue((second / "task-brief.md").exists())

    def test_manifest_json_describes_public_command_surface(self) -> None:
        payload = json.loads(run_aih("manifest", "--json").stdout)

        self.assertEqual(payload["name"], "Dmitriy AI Harness")
        self.assertIn("manifest", payload["commands"])
        self.assertIn("release", payload["commands"])
        self.assertIn("install-shell", payload["commands"])
        self.assertIn("latest-run", payload["commands"])
        self.assertIn("route", payload["commands"])
        self.assertIn("validate", payload["commands"])
        self.assertIn("implementation", payload["modes"])
        self.assertGreaterEqual(payload["file_counts"]["templates"], 8)

    def test_validate_json_runs_doctor_self_tests_and_manifest_gate(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_minimal_harness(root)
            tests = root / "tests"
            tests.mkdir()
            (tests / "test_smoke.py").write_text(
                "import unittest\n\n"
                "class SmokeTest(unittest.TestCase):\n"
                "    def test_truth(self):\n"
                "        self.assertTrue(True)\n"
            )
            payload = json.loads(run_aih("validate", "--json", env={"AI_HARNESS_HOME": temp_dir}).stdout)

        self.assertTrue(payload["ok"])
        self.assertTrue(payload["doctor_ok"])
        self.assertTrue(payload["self_tests_ok"])
        self.assertIn("validate", payload["manifest_commands"])

    def test_route_json_previews_routing_without_generating_prompt(self) -> None:
        payload = json.loads(run_aih("route", "fix", "the", "harness", "--json").stdout)

        self.assertEqual(payload["mode"], "implementation")
        self.assertEqual(payload["target"], "codex")
        self.assertEqual(payload["risk"], "normal")
        self.assertFalse(payload["deep_execution"])

    def test_route_json_redacts_secret_like_values(self) -> None:
        payload = json.loads(run_aih("route", "debug", "api_key=super-secret-token", "--json").stdout)

        self.assertEqual(payload["request"], "debug [REDACTED]")

    def test_human_output_can_use_color_without_coloring_json(self) -> None:
        human = run_aih("route", "fix", "the", "harness", env={"AIH_COLOR": "always"})
        machine = run_aih("route", "fix", "the", "harness", "--json", env={"AIH_COLOR": "always"})

        self.assertIn("\033[", human.stdout)
        self.assertNotIn("\033[", machine.stdout)
        self.assertEqual(json.loads(machine.stdout)["mode"], "implementation")

    def test_install_shell_writes_punctuation_safe_zsh_options(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / "env.sh"
            result = run_aih("install-shell", "--path", str(env_path))

            text = env_path.read_text()
            self.assertIn("unsetopt nomatch bare_glob_qual", text)
            self.assertIn("AIH shell punctuation fix installed", result.stdout)

            second = run_aih("install-shell", "--path", str(env_path))
            self.assertIn("already installed", second.stdout)

    def test_installed_zsh_options_allow_unquoted_punctuation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / "env.sh"
            run_aih("install-shell", "--path", str(env_path))
            result = subprocess.run(
                [
                    "zsh",
                    "-f",
                    "-lc",
                    f"source {env_path}; {AIH} prompt fix this (with parens) [brackets] question?",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=True,
            )

        self.assertIn("fix this (with parens) [brackets] question?", result.stdout)

    def test_release_creates_validation_packet(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_minimal_harness(root)
            tests = root / "tests"
            tests.mkdir()
            (tests / "test_smoke.py").write_text(
                "import unittest\n\n"
                "class SmokeTest(unittest.TestCase):\n"
                "    def test_truth(self):\n"
                "        self.assertTrue(True)\n"
            )

            release_dir = Path(run_aih("release", "candidate", env={"AI_HARNESS_HOME": temp_dir}).stdout.strip())

            self.assertTrue((release_dir / "doctor.json").exists())
            self.assertTrue((release_dir / "manifest.json").exists())
            self.assertTrue((release_dir / "self-test.log").exists())
            self.assertTrue((release_dir / "validation.md").exists())
            self.assertIn("Production Gates", (release_dir / "validation.md").read_text())
            self.assertIn("OK", (release_dir / "self-test.log").read_text())


if __name__ == "__main__":
    unittest.main()
