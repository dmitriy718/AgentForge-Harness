"""Additional tests to reach 97% coverage."""

from __future__ import annotations

import argparse
import sys
import unittest
from pathlib import Path
from unittest import mock

from aih import cli
from aih import doctor
from aih import agents


class CoverageGapTests(unittest.TestCase):
    def setUp(self) -> None:
        self.parser = cli.build_parser()

    @mock.patch("aih.cli.doctor_payload")
    def test_cmd_doctor_text(self, mock_doc: mock.MagicMock) -> None:
        mock_doc.return_value = ({"checks": [{"status": "OK", "name": "test", "detail": "test detail"}], "root": "/", "version": "1.0", "strict": False}, False)
        args = self.parser.parse_args(["doctor"])
        with self.assertRaises(SystemExit) as ctx:
            args.func(args)
        self.assertEqual(ctx.exception.code, 0)

    def test_cmd_manifest_text(self) -> None:
        args = self.parser.parse_args(["manifest"])
        args.func(args)

    @mock.patch("aih.cli.write_run")
    @mock.patch("aih.cli.overlay_from_args")
    @mock.patch("subprocess.run")
    def test_cmd_do_normal(self, mock_sub: mock.MagicMock, mock_overlay: mock.MagicMock, mock_write: mock.MagicMock) -> None:
        from aih.routing import Overlay
        mock_sub.return_value.returncode = 0
        mock_overlay.return_value = (Overlay("test", "test", "test", Path("/tmp"), "normal"), "prompt")
        mock_write.return_value = Path("/tmp/run")
        args = self.parser.parse_args(["do", "test"])
        args.func(args)

    @mock.patch("subprocess.run")
    def test_doctor_run_self_tests(self, mock_sub: mock.MagicMock) -> None:
        mock_sub.return_value.returncode = 0
        res = doctor.run_self_tests()
        self.assertEqual(res.returncode, 0)

    @mock.patch("aih.doctor.run_self_tests")
    @mock.patch("aih.doctor.doctor_payload")
    def test_doctor_validation_payload(self, mock_doc: mock.MagicMock, mock_tests: mock.MagicMock) -> None:
        mock_doc.return_value = ({"checks": []}, False)
        mock_tests.return_value.returncode = 0
        mock_tests.return_value.stdout = "ok"
        mock_tests.return_value.stderr = ""
        payload, failed = doctor.validation_payload()
        self.assertFalse(failed)
        self.assertTrue(payload["ok"])

    def test_manager_unknown_agent(self) -> None:
        from aih.agents.manager import get_agent
        with self.assertRaises(ValueError):
            get_agent("unknown_agent_123")

    @mock.patch.dict("sys.modules", {"tomllib": None, "tomli": None})
    def test_config_parse_toml_errors(self) -> None:
        from aih.config import _parse_toml
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "bad.toml"
            p.write_text("]bad toml[")
            res = _parse_toml(p)
            self.assertEqual(res, {})

    @mock.patch("aih.config.SEARCH_DIRS", ["does_not_exist"])
    def test_config_files(self) -> None:
        from aih.config import files
        res = files()
        self.assertEqual(res, [])

if __name__ == "__main__":
    unittest.main()
