import json
import os
from pathlib import Path
from contextlib import redirect_stdout, redirect_stderr
import io
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from agent_maker.cli import main


class CliTests(unittest.TestCase):
    def test_run_writes_proposal_and_scaffold(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest = root / "manifest.json"
            activities = root / "activities.jsonl"
            out_dir = root / "out"

            manifest.write_text(
                json.dumps(
                    {
                        "sources": [
                            {
                                "source_id": "outlook",
                                "name": "Outlook",
                                "category": "email",
                                "availability": "connected",
                                "approved": True,
                                "read_only": True,
                                "work_relevance": 0.9,
                                "identity_clarity": 0.9,
                                "structure": 0.8,
                                "signal_density": 0.85,
                                "noise_risk": 0.3,
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            activities.write_text(
                json.dumps(
                    {
                        "activity_id": "a1",
                        "source_id": "outlook",
                        "actor": "user",
                        "occurred_at": "2026-06-21T13:00:00Z",
                        "activity_type": "sent",
                        "object_type": "email",
                        "object_label": "Weekly status",
                        "summary": "Sent a weekly status update with blockers and next steps.",
                        "workflow_hints": ["email", "status"],
                        "confidence": 0.8,
                        "locator": "outlook:msg_1",
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main([
                    "run",
                    "--manifest",
                    str(manifest),
                    "--activities",
                    str(activities),
                    "--out",
                    str(out_dir),
                    "--allow-outside-scripts-output",
                ])

            self.assertEqual(exit_code, 0)
            self.assertTrue((out_dir / "source-report.md").exists())
            proposal_paths = list((out_dir / "proposals").glob("*.md"))
            scaffold_paths = list((out_dir / "scaffolds").glob("*.json"))
            self.assertTrue(proposal_paths)
            self.assertTrue(scaffold_paths)
            self.assertIn("## Blocked Actions", proposal_paths[0].read_text(encoding="utf-8"))
            scaffold = json.loads(scaffold_paths[0].read_text(encoding="utf-8"))
            self.assertFalse(scaffold["memory_policy"]["retain_raw_content"])
            self.assertIn("scorecard", scaffold)

    def test_rejects_output_outside_safe_root_by_default(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest = root / "manifest.json"
            out_dir = root / "out"
            manifest.write_text(json.dumps({"sources": []}), encoding="utf-8")

            with self.assertRaises(SystemExit):
                main(["run", "--manifest", str(manifest), "--out", str(out_dir)])

    def test_rejects_non_empty_output_without_overwrite(self):
        with TemporaryDirectory() as home_dir, patch.dict(os.environ, {"HOME": home_dir}):
            safe_root = Path.home() / "scripts_output" / "agent-maker" / "test-existing-output"
            safe_root.mkdir(parents=True, exist_ok=True)
            marker = safe_root / "marker.txt"
            marker.write_text("existing", encoding="utf-8")
            with TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                manifest = root / "manifest.json"
                manifest.write_text(json.dumps({"sources": []}), encoding="utf-8")

                with self.assertRaises(SystemExit):
                    main(["run", "--manifest", str(manifest), "--out", str(safe_root)])

    def test_overwrite_clears_stale_managed_outputs(self):
        with TemporaryDirectory() as home_dir, patch.dict(os.environ, {"HOME": home_dir}):
            safe_root = Path.home() / "scripts_output" / "agent-maker" / "test-overwrite-output"
            stale_proposals = safe_root / "proposals"
            stale_scaffolds = safe_root / "scaffolds"
            stale_proposals.mkdir(parents=True, exist_ok=True)
            stale_scaffolds.mkdir(parents=True, exist_ok=True)
            (stale_proposals / "stale.md").write_text("stale", encoding="utf-8")
            (stale_scaffolds / "stale.json").write_text("stale", encoding="utf-8")
            with TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                manifest = root / "manifest.json"
                manifest.write_text(json.dumps({"sources": []}), encoding="utf-8")

                with redirect_stdout(io.StringIO()):
                    main(["run", "--manifest", str(manifest), "--out", str(safe_root), "--overwrite"])

                self.assertFalse((stale_proposals / "stale.md").exists())
                self.assertFalse((stale_scaffolds / "stale.json").exists())
                self.assertTrue((safe_root / ".agent-maker-run").exists())

    def test_rejects_overwrite_outside_safe_root_without_marker(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest = root / "manifest.json"
            out_dir = root / "out"
            proposals = out_dir / "proposals"
            proposals.mkdir(parents=True)
            (proposals / "unrelated.md").write_text("keep me", encoding="utf-8")
            manifest.write_text(json.dumps({"sources": []}), encoding="utf-8")

            with self.assertRaises(SystemExit):
                main([
                    "run",
                    "--manifest",
                    str(manifest),
                    "--out",
                    str(out_dir),
                    "--overwrite",
                    "--allow-outside-scripts-output",
                ])

            self.assertTrue((proposals / "unrelated.md").exists())

    def test_allows_overwrite_outside_safe_root_with_marker(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest = root / "manifest.json"
            out_dir = root / "out"
            proposals = out_dir / "proposals"
            proposals.mkdir(parents=True)
            (out_dir / ".agent-maker-run").write_text("agent-maker-output\n", encoding="utf-8")
            (proposals / "stale.md").write_text("stale", encoding="utf-8")
            manifest.write_text(json.dumps({"sources": []}), encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                exit_code = main([
                    "run",
                    "--manifest",
                    str(manifest),
                    "--out",
                    str(out_dir),
                    "--overwrite",
                    "--allow-outside-scripts-output",
                ])

            self.assertEqual(exit_code, 0)
            self.assertFalse((proposals / "stale.md").exists())
            self.assertEqual((out_dir / ".agent-maker-run").stat().st_mode & 0o777, 0o600)

    def test_safe_output_parent_is_private(self):
        with TemporaryDirectory() as home_dir, patch.dict(os.environ, {"HOME": home_dir}):
            safe_root = Path.home() / "scripts_output" / "agent-maker" / "test-private-output"
            with TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                manifest = root / "manifest.json"
                manifest.write_text(json.dumps({"sources": []}), encoding="utf-8")

                with redirect_stdout(io.StringIO()):
                    main(["run", "--manifest", str(manifest), "--out", str(safe_root), "--overwrite"])

                agent_maker_root = Path.home() / "scripts_output" / "agent-maker"
                self.assertEqual(agent_maker_root.stat().st_mode & 0o777, 0o700)
                self.assertEqual(safe_root.stat().st_mode & 0o777, 0o700)

    def test_rejects_invalid_limit_values(self):
        for value in ("0", "-1", "4"):
            with self.subTest(value=value):
                with self.assertRaises(SystemExit), redirect_stderr(io.StringIO()):
                    main(["run", "--manifest", "unused.json", "--limit", value])

    def test_invalid_jsonl_prints_clean_error(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest = root / "manifest.json"
            activities = root / "bad.jsonl"
            out_dir = root / "out"
            manifest.write_text(json.dumps({"sources": []}), encoding="utf-8")
            activities.write_text("{bad json}\n", encoding="utf-8")
            stderr = io.StringIO()

            with self.assertRaises(SystemExit) as context, redirect_stderr(stderr):
                main([
                    "run",
                    "--manifest",
                    str(manifest),
                    "--activities",
                    str(activities),
                    "--out",
                    str(out_dir),
                    "--allow-outside-scripts-output",
                ])

            self.assertEqual(context.exception.code, 1)
            self.assertIn("agent-maker: error: invalid JSONL at line 1", stderr.getvalue())

    def test_wrong_shape_jsonl_prints_clean_error(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest = root / "manifest.json"
            activities = root / "bad.jsonl"
            out_dir = root / "out"
            manifest.write_text(json.dumps({"sources": []}), encoding="utf-8")
            activities.write_text("[]\n", encoding="utf-8")
            stderr = io.StringIO()

            with self.assertRaises(SystemExit) as context, redirect_stderr(stderr):
                main([
                    "run",
                    "--manifest",
                    str(manifest),
                    "--activities",
                    str(activities),
                    "--out",
                    str(out_dir),
                    "--allow-outside-scripts-output",
                ])

            self.assertEqual(context.exception.code, 1)
            self.assertIn("agent-maker: error: invalid JSONL at line 1: expected object", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
