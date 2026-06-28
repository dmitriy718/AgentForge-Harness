"""Tests for aih.doctor — doctor_payload, build_manifest, validation_payload."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from aih import config as cfg
from aih.doctor import Check, doctor_checks, doctor_payload, build_manifest


class CheckTests(unittest.TestCase):
    def test_ok_status(self) -> None:
        c = Check("test", True, "detail")
        self.assertEqual(c.status, "OK")

    def test_fail_status(self) -> None:
        c = Check("test", False, "detail", required=True)
        self.assertEqual(c.status, "FAIL")

    def test_warn_status(self) -> None:
        c = Check("test", False, "detail", required=False)
        self.assertEqual(c.status, "WARN")

    def test_frozen_dataclass(self) -> None:
        c = Check("test", True, "detail")
        with self.assertRaises(AttributeError):
            c.name = "other"  # type: ignore[misc]


class DoctorChecksTests(unittest.TestCase):
    def test_returns_checks(self) -> None:
        checks = doctor_checks()
        self.assertIsInstance(checks, list)
        self.assertTrue(len(checks) > 0)
        self.assertTrue(all(isinstance(c, Check) for c in checks))

    def test_root_exists_check(self) -> None:
        checks = doctor_checks()
        root_check = next(c for c in checks if c.name == "root exists")
        self.assertTrue(root_check.ok)

    def test_strict_mode_adds_requirements(self) -> None:
        checks_normal = doctor_checks(strict=False)
        checks_strict = doctor_checks(strict=True)
        # Strict mode should make codex cli required
        codex_check_normal = next(c for c in checks_normal if "codex cli" in c.name)
        codex_check_strict = next(c for c in checks_strict if "codex cli" in c.name)
        self.assertFalse(codex_check_normal.required)
        self.assertTrue(codex_check_strict.required)


class DoctorPayloadTests(unittest.TestCase):
    def test_payload_structure(self) -> None:
        payload, failed = doctor_payload()
        self.assertIn("ok", payload)
        self.assertIn("strict", payload)
        self.assertIn("root", payload)
        self.assertIn("version", payload)
        self.assertIn("checks", payload)
        self.assertIn("generated_at", payload)

    def test_payload_checks_are_dicts(self) -> None:
        payload, _ = doctor_payload()
        checks = payload["checks"]
        self.assertIsInstance(checks, list)
        for check in checks:  # type: ignore[union-attr]
            self.assertIn("name", check)
            self.assertIn("status", check)
            self.assertIn("ok", check)


class BuildManifestTests(unittest.TestCase):
    def test_manifest_structure(self) -> None:
        manifest = build_manifest()
        self.assertEqual(manifest["name"], "Dmitriy AI Harness")
        self.assertIn("commands", manifest)
        self.assertIn("modes", manifest)
        self.assertIn("version", manifest)
        self.assertIn("do", manifest["commands"])
        self.assertIn("implementation", manifest["modes"])

    def test_manifest_has_all_expected_commands(self) -> None:
        manifest = build_manifest()
        commands = manifest["commands"]
        expected = {"ask", "do", "doctor", "manifest", "release", "validate", "route", "health"}
        for cmd in expected:
            self.assertIn(cmd, commands)

    def test_manifest_has_search_dirs(self) -> None:
        manifest = build_manifest()
        self.assertIn("search_dirs", manifest)
        self.assertIn("file_counts", manifest)


if __name__ == "__main__":
    unittest.main()
