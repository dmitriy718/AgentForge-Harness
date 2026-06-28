"""Tests for aih.release — release packet generation."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from aih import config as cfg
from aih.release import create_release


class CreateReleaseTests(unittest.TestCase):
    @mock.patch("aih.release.run_self_tests")
    def test_create_release(self, mock_run: mock.MagicMock) -> None:
        mock_result = mock.MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "tests passed\n"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        with tempfile.TemporaryDirectory() as tmp:
            old_root = cfg.ROOT
            cfg.set_root(Path(tmp))
            try:
                # We need to mock doctor_payload since we're in a tmp dir
                with mock.patch("aih.release.doctor_payload") as mock_doctor:
                    mock_doctor.return_value = ({"checks": []}, False)
                    with mock.patch("aih.release.build_manifest") as mock_manifest:
                        mock_manifest.return_value = {"name": "test"}

                        release_dir, failed = create_release("test-release", show_progress=False)

                        self.assertFalse(failed)
                        self.assertTrue(release_dir.exists())
                        self.assertTrue((release_dir / "doctor.json").exists())
                        self.assertTrue((release_dir / "manifest.json").exists())
                        self.assertTrue((release_dir / "self-test.log").exists())
                        self.assertTrue((release_dir / "validation.md").exists())
                        
                        # Verify content
                        tests_log = (release_dir / "self-test.log").read_text()
                        self.assertIn("tests passed", tests_log)
                        
                        validation = (release_dir / "validation.md").read_text()
                        self.assertIn("test-release", validation)
                        self.assertIn("Doctor passed: True", validation)
                        self.assertIn("Self-tests passed: True", validation)
            finally:
                cfg.set_root(old_root)

    @mock.patch("aih.release.run_self_tests")
    def test_create_release_fails_when_doctor_fails(self, mock_run: mock.MagicMock) -> None:
        mock_result = mock.MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        with tempfile.TemporaryDirectory() as tmp:
            old_root = cfg.ROOT
            cfg.set_root(Path(tmp))
            try:
                with mock.patch("aih.release.doctor_payload") as mock_doctor:
                    # Doctor failed
                    mock_doctor.return_value = ({"checks": []}, True)
                    with mock.patch("aih.release.build_manifest") as mock_manifest:
                        mock_manifest.return_value = {"name": "test"}

                        release_dir, failed = create_release("test-release", show_progress=False)

                        self.assertTrue(failed)
                        validation = (release_dir / "validation.md").read_text()
                        self.assertIn("Doctor passed: False", validation)
            finally:
                cfg.set_root(old_root)


if __name__ == "__main__":
    unittest.main()
