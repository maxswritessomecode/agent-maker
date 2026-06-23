import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from agent_maker.core import load_manifest, score_source


class SourceScoringTests(unittest.TestCase):
    def test_scores_approved_read_only_high_signal_source_as_primary(self):
        source = load_manifest(_manifest_path([
            {
                "source_id": "teams",
                "name": "Teams",
                "category": "chat",
                "availability": "connected",
                "approved": True,
                "read_only": True,
                "work_relevance": 0.95,
                "identity_clarity": 0.9,
                "structure": 0.8,
                "signal_density": 0.9,
                "noise_risk": 0.2,
                "evidence_quality": {
                    "has_stable_ids": True,
                    "has_timestamps": True,
                    "has_authors": True,
                    "has_links": True,
                },
            }
        ]))[0]

        score = score_source(source)

        self.assertEqual(score.status, "primary")
        self.assertGreaterEqual(score.score, 0.8)

    def test_excludes_unapproved_source(self):
        source = load_manifest(_manifest_path([
            {
                "source_id": "drive",
                "name": "Drive",
                "category": "docs",
                "availability": "connected",
                "approved": False,
                "read_only": True,
            }
        ]))[0]

        score = score_source(source)

        self.assertEqual(score.status, "excluded")
        self.assertEqual(score.score, 0.0)

    def test_string_false_does_not_become_truthy(self):
        source = load_manifest(_manifest_path([
            {
                "source_id": "slack",
                "name": "Slack",
                "category": "chat",
                "availability": "connected",
                "approved": "false",
                "read_only": "true",
                "work_relevance": 0.9,
                "signal_density": 0.9,
            }
        ]))[0]

        score = score_source(source)

        self.assertEqual(score.status, "excluded")

    def test_rejects_ambiguous_boolean_strings(self):
        with self.assertRaises(ValueError):
            load_manifest(_manifest_path([
                {
                    "source_id": "slack",
                    "name": "Slack",
                    "category": "chat",
                    "availability": "connected",
                    "approved": "yes",
                    "read_only": True,
                }
            ]))

    def test_accepts_top_level_source_list_manifest(self):
        source = load_manifest(_raw_manifest_path([
            {
                "source_id": "calendar",
                "name": "Calendar",
                "category": "calendar",
                "availability": "export_only",
                "approved": True,
                "read_only": True,
            }
        ]))[0]

        self.assertEqual(source.source_id, "calendar")

    def test_rejects_object_manifest_without_sources_key(self):
        with self.assertRaisesRegex(ValueError, "manifest must contain a sources list"):
            load_manifest(_raw_manifest_path({}))

    def test_excludes_secret_source(self):
        source = load_manifest(_manifest_path([
            {
                "source_id": "secrets",
                "name": "Secrets",
                "category": "files",
                "availability": "local_path",
                "approved": True,
                "read_only": True,
                "privacy_class": "secret",
            }
        ]))[0]

        score = score_source(source)

        self.assertEqual(score.status, "excluded")

    def test_normalizes_privacy_class(self):
        source = load_manifest(_manifest_path([
            {
                "source_id": "secrets",
                "name": "Secrets",
                "category": "files",
                "availability": "local_path",
                "approved": True,
                "read_only": True,
                "privacy_class": " Secret ",
            }
        ]))[0]

        self.assertEqual(source.privacy_class, "secret")

    def test_rejects_unknown_privacy_class(self):
        with self.assertRaises(ValueError):
            load_manifest(_manifest_path([
                {
                    "source_id": "unknown",
                    "name": "Unknown",
                    "category": "files",
                    "availability": "local_path",
                    "approved": True,
                    "read_only": True,
                    "privacy_class": "mystery",
                }
            ]))

    def test_wraps_malformed_manifest_record_errors(self):
        with self.assertRaisesRegex(ValueError, "invalid manifest source at index 1"):
            load_manifest(_raw_manifest_path([[]]))

        with self.assertRaisesRegex(ValueError, "invalid manifest source at index 1"):
            load_manifest(_raw_manifest_path([{"name": "Missing ID"}]))

    def test_rejects_duplicate_source_ids(self):
        with self.assertRaisesRegex(ValueError, "duplicate source_id: drive"):
            load_manifest(_raw_manifest_path([
                {
                    "source_id": "drive",
                    "name": "Secret Drive",
                    "category": "docs",
                    "availability": "connected",
                    "approved": True,
                    "read_only": True,
                    "privacy_class": "secret",
                },
                {
                    "source_id": "drive",
                    "name": "Work Drive",
                    "category": "docs",
                    "availability": "connected",
                    "approved": True,
                    "read_only": True,
                    "privacy_class": "internal_work",
                },
            ]))


def _manifest_path(sources):
    return _raw_manifest_path({"sources": sources})


def _raw_manifest_path(payload):
    temp = TemporaryDirectory()
    path = Path(temp.name) / "manifest.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    _TEMP_DIRS.append(temp)
    return path


_TEMP_DIRS = []


if __name__ == "__main__":
    unittest.main()
