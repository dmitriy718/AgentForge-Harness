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
        self.assertIn("implementation", payload["modes"])
        self.assertGreaterEqual(payload["file_counts"]["templates"], 8)

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
