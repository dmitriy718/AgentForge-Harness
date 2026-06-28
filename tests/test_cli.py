"""Tests for aih.cli — command line interface handlers."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from aih import config as cfg
from aih import cli


class CliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.parser = cli.build_parser()

    @mock.patch("aih.cli.write_run")
    @mock.patch("subprocess.run")
    def test_cmd_do(self, mock_sub: mock.MagicMock, mock_write: mock.MagicMock) -> None:
        mock_sub.return_value.returncode = 0
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "run"
            run_dir.mkdir()
            mock_write.return_value = run_dir
            
            args = self.parser.parse_args(["do", "fix", "the", "bug"])
            with self.assertRaises(SystemExit) as ctx:
                args.func(args)
            self.assertEqual(ctx.exception.code, 0)
            mock_write.assert_called_once()
            mock_sub.assert_called_once()

    @mock.patch("aih.cli.write_run")
    def test_cmd_ask_save(self, mock_write: mock.MagicMock) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "run"
            run_dir.mkdir()
            mock_write.return_value = run_dir
            
            args = self.parser.parse_args(["ask", "fix", "bug", "--save"])
            # Should just return without exception
            args.func(args)
            mock_write.assert_called_once()

    @mock.patch("aih.cli.write_run")
    def test_cmd_run(self, mock_write: mock.MagicMock) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "run"
            run_dir.mkdir()
            mock_write.return_value = run_dir
            
            args = self.parser.parse_args(["run", "fix", "bug"])
            args.func(args)
            mock_write.assert_called_once()

    def test_cmd_route(self) -> None:
        args = self.parser.parse_args(["route", "fix", "bug"])
        # Should execute and print normally
        args.func(args)

    def test_cmd_route_json(self) -> None:
        args = self.parser.parse_args(["route", "fix", "bug", "--json"])
        args.func(args)

    @mock.patch("aih.cli.doctor_payload")
    def test_cmd_doctor_json(self, mock_doctor: mock.MagicMock) -> None:
        mock_doctor.return_value = ({"checks": []}, False)
        args = self.parser.parse_args(["doctor", "--json"])
        with self.assertRaises(SystemExit) as ctx:
            args.func(args)
        self.assertEqual(ctx.exception.code, 0)

    @mock.patch("aih.cli.validation_payload")
    def test_cmd_validate_json(self, mock_val: mock.MagicMock) -> None:
        mock_val.return_value = ({"ok": True, "manifest_commands": [], "root": "/", "version": "1.0", "strict": False, "doctor_ok": True, "self_tests_ok": True, "self_tests_exit_code": 0}, False)
        args = self.parser.parse_args(["validate", "--json"])
        with self.assertRaises(SystemExit) as ctx:
            args.func(args)
        self.assertEqual(ctx.exception.code, 0)

    @mock.patch("aih.cli.validation_payload")
    def test_cmd_validate_text(self, mock_val: mock.MagicMock) -> None:
        mock_val.return_value = ({"ok": True, "manifest_commands": [], "root": "/", "version": "1.0", "strict": False, "doctor_ok": True, "self_tests_ok": True, "self_tests_exit_code": 0}, False)
        args = self.parser.parse_args(["validate"])
        with self.assertRaises(SystemExit) as ctx:
            args.func(args)
        self.assertEqual(ctx.exception.code, 0)

    @mock.patch("aih.cli.create_release")
    def test_cmd_release(self, mock_rel: mock.MagicMock) -> None:
        mock_rel.return_value = (Path("/tmp"), False)
        args = self.parser.parse_args(["release", "test-release"])
        args.func(args)

    @mock.patch("aih.cli.create_release")
    def test_cmd_release_fails(self, mock_rel: mock.MagicMock) -> None:
        mock_rel.return_value = (Path("/tmp"), True)
        args = self.parser.parse_args(["release", "test-release"])
        with self.assertRaises(SystemExit) as ctx:
            args.func(args)
        self.assertEqual(ctx.exception.code, 1)

    @mock.patch("aih.cli.write_health_snapshot")
    def test_cmd_health(self, mock_health: mock.MagicMock) -> None:
        mock_health.return_value = (Path("/tmp"), {"metrics": {}})
        args = self.parser.parse_args(["health"])
        args.func(args)

    @mock.patch("aih.cli.write_health_snapshot")
    def test_cmd_health_json(self, mock_health: mock.MagicMock) -> None:
        mock_health.return_value = (Path("/tmp"), {"metrics": {}})
        args = self.parser.parse_args(["health", "--json"])
        args.func(args)

    def test_cmd_manifest(self) -> None:
        args = self.parser.parse_args(["manifest", "--json"])
        args.func(args)

    @mock.patch("aih.cli.cfg.files")
    def test_cmd_list(self, mock_files: mock.MagicMock) -> None:
        mock_files.return_value = [cfg.ROOT / "test.md"]
        args = self.parser.parse_args(["list"])
        args.func(args)

    @mock.patch("aih.cli.cfg.match_file")
    def test_cmd_show(self, mock_match: mock.MagicMock) -> None:
        mock_path = mock.MagicMock()
        mock_path.read_text.return_value = "content"
        mock_match.return_value = mock_path
        args = self.parser.parse_args(["show", "test"])
        args.func(args)

    @mock.patch("aih.audit.unique_run_dir")
    @mock.patch("shutil.copyfile")
    def test_cmd_new_run(self, mock_copy: mock.MagicMock, mock_unique: mock.MagicMock) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "run"
            mock_unique.return_value = run_dir
            args = self.parser.parse_args(["new-run", "test"])
            args.func(args)

    @mock.patch("aih.cli.install_shell_config")
    def test_cmd_install_shell(self, mock_install: mock.MagicMock) -> None:
        mock_install.return_value = True
        args = self.parser.parse_args(["install-shell"])
        args.func(args)
        
        args = self.parser.parse_args(["install-shell", "--path", "/tmp/env.sh"])
        args.func(args)

    @mock.patch("aih.cli.cfg.match_file")
    def test_cmd_compile(self, mock_match: mock.MagicMock) -> None:
        mock_path = mock.MagicMock()
        mock_path.read_text.return_value = "template"
        mock_path.relative_to.return_value = Path("template")
        mock_match.return_value = mock_path
        with tempfile.TemporaryDirectory() as tmp:
            brief = Path(tmp) / "brief.md"
            brief.write_text("brief content")
            args = self.parser.parse_args(["compile", "template", str(brief)])
            args.func(args)

    @mock.patch("aih.cli.cfg.match_file")
    def test_cmd_compile_out(self, mock_match: mock.MagicMock) -> None:
        mock_path = mock.MagicMock()
        mock_path.read_text.return_value = "template"
        mock_path.relative_to.return_value = Path("template")
        mock_match.return_value = mock_path
        with tempfile.TemporaryDirectory() as tmp:
            brief = Path(tmp) / "brief.md"
            brief.write_text("brief content")
            out = Path(tmp) / "out.md"
            args = self.parser.parse_args(["compile", "template", str(brief), "--out", str(out)])
            args.func(args)

    def test_cmd_latest_run_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            old_root = cfg.ROOT
            cfg.set_root(Path(tmp))
            try:
                args = self.parser.parse_args(["latest-run"])
                with self.assertRaises(SystemExit):
                    args.func(args)
            finally:
                cfg.set_root(old_root)

    def test_cmd_latest_run_success(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            old_root = cfg.ROOT
            cfg.set_root(Path(tmp))
            try:
                run_dir = Path(tmp) / "runs" / "test"
                run_dir.mkdir(parents=True)
                (run_dir / "metadata.txt").write_text("mode=test\n")
                args = self.parser.parse_args(["latest-run"])
                args.func(args)
                
                args_json = self.parser.parse_args(["latest-run", "--json"])
                args_json.func(args_json)
            finally:
                cfg.set_root(old_root)

    @mock.patch("aih.cli.overlay_from_args")
    def test_cmd_ask_out(self, mock_overlay: mock.MagicMock) -> None:
        from aih.routing import Overlay
        mock_overlay.return_value = (Overlay("test", "test", "test", Path("/"), "normal"), "prompt")
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out.md"
            args = self.parser.parse_args(["ask", "test", "--out", str(out)])
            args.func(args)

    @mock.patch("aih.cli.overlay_from_args")
    def test_cmd_do_dry_run(self, mock_overlay: mock.MagicMock) -> None:
        from aih.routing import Overlay
        mock_overlay.return_value = (Overlay("test", "test", "test", Path("/tmp"), "normal"), "prompt")
        args = self.parser.parse_args(["do", "test", "--dry-run"])
        args.func(args)

    @mock.patch("aih.cli.overlay_from_args")
    @mock.patch("shutil.which")
    def test_cmd_do_no_codex(self, mock_which: mock.MagicMock, mock_overlay: mock.MagicMock) -> None:
        from aih.routing import Overlay
        mock_overlay.return_value = (Overlay(mode="codex", target="codex", risk="test", cwd=Path("/tmp"), request="normal"), "prompt")
        mock_which.return_value = None
        args = self.parser.parse_args(["do", "test", "--target", "codex"])
        with mock.patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(SystemExit):
                args.func(args)

    @mock.patch("aih.cli.write_run")
    @mock.patch("aih.cli.overlay_from_args")
    @mock.patch("subprocess.run")
    def test_cmd_do_deep(self, mock_sub: mock.MagicMock, mock_overlay: mock.MagicMock, mock_write: mock.MagicMock) -> None:
        from aih.routing import Overlay
        mock_sub.return_value.returncode = 0
        mock_overlay.return_value = (Overlay(mode="codex", target="codex", risk="test", cwd=Path("/tmp"), request="normal"), "prompt")
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "run"
            run_dir.mkdir()
            mock_write.return_value = run_dir
            args = self.parser.parse_args(["do", "a" * 1000])
            with self.assertRaises(SystemExit):
                args.func(args)

    @mock.patch("aih.cli.overlay_from_args")
    def test_cmd_ask_normal(self, mock_overlay: mock.MagicMock) -> None:
        from aih.routing import Overlay
        mock_overlay.return_value = (Overlay(mode="test", target="test", risk="test", cwd=Path("/tmp"), request="normal"), "prompt")
        args = self.parser.parse_args(["ask", "test"])
        args.func(args)

    @mock.patch("aih.cli.sys.argv", ["aih", "health"])
    @mock.patch("aih.cli.write_health_snapshot")
    def test_main(self, mock_health: mock.MagicMock) -> None:
        mock_health.return_value = (Path("/tmp"), {})
        cli.main()

    @mock.patch("aih.cli.sys.argv", ["aih"])
    def test_main_no_args(self) -> None:
        with self.assertRaises(SystemExit) as ctx:
            cli.main_entry()
        self.assertEqual(ctx.exception.code, 0)

if __name__ == "__main__":
    unittest.main()
