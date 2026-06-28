"""Tests for aih.health — system health snapshot."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from aih import config as cfg


class WriteHealthSnapshotTests(unittest.TestCase):
    def test_creates_snapshot_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            old_root = cfg.ROOT
            cfg.set_root(Path(tmp))
            try:
                from aih.health import write_health_snapshot

                out, results = write_health_snapshot()
                self.assertTrue(out.exists())
                self.assertIn("health-", out.name)
                content = out.read_text()
                # Should contain at least one command header
                self.assertIn("$ ", content)
                self.assertIn("metrics", results)
            finally:
                cfg.set_root(old_root)

    def test_snapshot_dir_created(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            old_root = cfg.ROOT
            cfg.set_root(Path(tmp))
            try:
                from aih.health import write_health_snapshot

                out, _ = write_health_snapshot()
                self.assertTrue(out.parent.exists())
                self.assertEqual(out.parent.name, "system-health")
            finally:
                cfg.set_root(old_root)


if __name__ == "__main__":
    unittest.main()
