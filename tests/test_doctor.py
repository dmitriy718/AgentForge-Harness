"""Unit tests for aih.doctor — direct imports, no subprocess."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from aih import config as cfg
from aih.doctor import Check, doctor_checks, build_manifest


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


class BuildManifestTests(unittest.TestCase):
    def test_manifest_structure(self) -> None:
        manifest = build_manifest()
        self.assertEqual(manifest["name"], "Dmitriy AI Harness")
        self.assertIn("commands", manifest)
        self.assertIn("modes", manifest)
        self.assertIn("version", manifest)
        self.assertIn("do", manifest["commands"])
        self.assertIn("implementation", manifest["modes"])


if __name__ == "__main__":
    unittest.main()
