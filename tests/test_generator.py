import unittest

from agent_maker.core import Activity, Source
from agent_maker.core import activity_from_dict
from agent_maker.generator import generate_proposals


class ProposalGenerationTests(unittest.TestCase):
    def test_generates_meeting_followup_proposal_from_meeting_activity(self):
        sources = [
            Source(
                source_id="calendar",
                name="Calendar",
                category="calendar",
                availability="connected",
                approved=True,
                read_only=True,
                work_relevance=0.9,
                identity_clarity=0.9,
                structure=0.9,
                signal_density=0.8,
                noise_risk=0.2,
            )
        ]
        activities = [
            Activity(
                activity_id="a1",
                source_id="calendar",
                actor="user",
                occurred_at="2026-06-20T10:00:00Z",
                activity_type="met",
                object_type="meeting",
                object_label="Launch sync",
                summary="Discussed launch follow-up and open action items.",
                workflow_hints=("meeting", "open-loop"),
                confidence=0.8,
                locator="calendar:event_1",
            )
        ]

        proposals = generate_proposals(sources, activities)

        self.assertEqual(len(proposals), 1)
        self.assertEqual(proposals[0].agent_name, "Meeting Follow-up Coordinator")
        self.assertIn("calendar", proposals[0].source_ids)
        self.assertEqual(proposals[0].opportunity_score, 3)
        self.assertLessEqual(proposals[0].confidence, 0.62)
        self.assertTrue(proposals[0].scorecard_details)
        self.assertIn("workflow_hint", proposals[0].scorecard_details[1].details[0])
        self.assertTrue(proposals[0].confidence_breakdown)
        self.assertIn("Avg activity confidence", proposals[0].confidence_breakdown[0])
        self.assertEqual(proposals[0].evidence_notes[0].classified_as, "meeting")
        self.assertTrue(proposals[0].evidence_notes[0].classification_signals)

    def test_blocks_hr_related_activity(self):
        sources = [
            Source("teams", "Teams", "chat", "connected", True, True, work_relevance=0.9, signal_density=0.9)
        ]
        activities = [
            Activity(
                activity_id="a1",
                source_id="teams",
                actor="user",
                occurred_at="2026-06-20T10:00:00Z",
                activity_type="reviewed",
                object_type="doc",
                object_label="Performance review",
                summary="Discussed performance review calibration.",
                workflow_hints=("performance-review",),
            )
        ]

        proposals = generate_proposals(sources, activities)

        self.assertEqual(proposals, [])

    def test_blocks_sensitive_activity_privacy_classes_even_when_source_is_approved(self):
        sources = [
            Source("teams", "Teams", "chat", "connected", True, True, work_relevance=0.9, signal_density=0.9)
        ]
        for privacy_class in ("secret", "regulated", "personal_sensitive"):
            with self.subTest(privacy_class=privacy_class):
                activities = [
                    Activity(
                        activity_id="a1",
                        source_id="teams",
                        actor="user",
                        occurred_at="2026-06-20T10:00:00Z",
                        activity_type="sent",
                        object_type="email",
                        object_label="Launch update",
                        summary="Routine status update.",
                        workflow_hints=("email", "status"),
                        privacy_class=privacy_class,
                    )
                ]

                proposals = generate_proposals(sources, activities)

                self.assertEqual(proposals, [])

    def test_clamps_proposal_limit_to_three_when_called_directly(self):
        sources = [
            Source("work", "Work", "docs", "connected", True, True, work_relevance=0.9, signal_density=0.9)
        ]
        activities = [
            Activity("a1", "work", "user", "2026-06-20", "met", "meeting", "Sync", "Meeting", ("meeting",)),
            Activity("a2", "work", "user", "2026-06-20", "sent", "email", "Email", "Email", ("email",)),
            Activity("a3", "work", "user", "2026-06-20", "drafted", "doc", "Status", "Status", ("status",)),
            Activity("a4", "work", "user", "2026-06-20", "edited", "ticket", "Task", "Task", ("project",)),
            Activity("a5", "work", "user", "2026-06-20", "decided", "memo", "Decision", "Decision", ("decision",)),
        ]

        proposals = generate_proposals(sources, activities, limit=5)

        self.assertEqual(len(proposals), 3)

    def test_blocks_sensitive_domain_text_without_hint(self):
        sources = [
            Source("drive", "Drive", "docs", "connected", True, True, work_relevance=0.9, signal_density=0.9)
        ]
        activities = [
            Activity(
                activity_id="a1",
                source_id="drive",
                actor="user",
                occurred_at="2026-06-20T10:00:00Z",
                activity_type="edited",
                object_type="doc",
                object_label="Promotion decision notes",
                summary="Drafted notes for a promotion decision.",
                workflow_hints=(),
            )
        ]

        proposals = generate_proposals(sources, activities)

        self.assertEqual(proposals, [])

    def test_blocks_sensitive_domain_text_with_separators(self):
        sources = [
            Source("drive", "Drive", "docs", "connected", True, True, work_relevance=0.9, signal_density=0.9)
        ]
        activities = [
            Activity(
                activity_id="a1",
                source_id="drive",
                actor="user",
                occurred_at="2026-06-20T10:00:00Z",
                activity_type="edited",
                object_type="doc",
                object_label="legal-advice notes",
                summary="Routine workspace note.",
                workflow_hints=(),
            ),
            Activity(
                activity_id="a2",
                source_id="drive",
                actor="user",
                occurred_at="2026-06-20T11:00:00Z",
                activity_type="edited",
                object_type="doc",
                object_label="performance_review notes",
                summary="Routine workspace note.",
                workflow_hints=(),
            ),
        ]

        proposals = generate_proposals(sources, activities)

        self.assertEqual(proposals, [])

    def test_blocks_sensitive_workflow_hint_string_variants(self):
        sources = [
            Source("drive", "Drive", "docs", "connected", True, True, work_relevance=0.9, signal_density=0.9)
        ]
        for hint in ("performance-review", "performance_review", "performance review", "hr,email", "hiring|email", "legal;email"):
            with self.subTest(hint=hint):
                activities = [
                    activity_from_dict(
                        {
                            "activity_id": "a1",
                            "source_id": "drive",
                            "actor": "user",
                            "occurred_at": "2026-06-20T10:00:00Z",
                            "activity_type": "reviewed",
                            "object_type": "doc",
                            "object_label": "Routine workspace note",
                            "summary": "Routine workspace note.",
                            "workflow_hints": hint,
                        }
                    )
                ]

                proposals = generate_proposals(sources, activities)

                self.assertEqual(proposals, [])

    def test_generates_sales_support_content_and_release_patterns(self):
        sources = [
            Source("crm", "CRM", "crm", "connected", True, True, work_relevance=0.9, signal_density=0.9),
            Source("support", "Support", "support", "connected", True, True, work_relevance=0.9, signal_density=0.9),
            Source("docs", "Docs", "docs", "connected", True, True, work_relevance=0.9, signal_density=0.9),
            Source("github", "GitHub", "code", "connected", True, True, work_relevance=0.9, signal_density=0.9),
        ]
        cases = [
            (
                Activity("a1", "crm", "user", "2026-06-20", "reviewed", "record", "Account call prep", "Prepared account brief.", ("sales", "crm")),
                "Account Briefing Assistant",
            ),
            (
                Activity("a2", "support", "user", "2026-06-20", "triaged", "ticket", "Escalation summary", "Grouped support escalation notes.", ("support", "escalation")),
                "Support Triage Assistant",
            ),
            (
                Activity("a3", "docs", "user", "2026-06-20", "drafted", "doc", "Newsletter outline", "Repurposed article into newsletter.", ("content", "newsletter")),
                "Content Repurposing Assistant",
            ),
            (
                Activity("a4", "github", "user", "2026-06-20", "reviewed", "pull_request", "Release notes", "Grouped merged work for release notes.", ("release", "pull-request")),
                "Release Notes Assistant",
            ),
        ]

        for activity, agent_name in cases:
            with self.subTest(agent_name=agent_name):
                proposals = generate_proposals(sources, [activity])

                self.assertEqual(proposals[0].agent_name, agent_name)

    def test_blocks_public_marketplace_hr_agent_patterns(self):
        sources = [
            Source("work", "Work", "docs", "connected", True, True, work_relevance=0.9, signal_density=0.9)
        ]
        for label in ("Resume screening agent", "Candidate ranking system", "Interview debrief collector", "New hire onboarding orchestrator"):
            with self.subTest(label=label):
                activities = [
                    Activity(
                        activity_id="a1",
                        source_id="work",
                        actor="user",
                        occurred_at="2026-06-20T10:00:00Z",
                        activity_type="reviewed",
                        object_type="doc",
                        object_label=label,
                        summary="Public template style HR workflow.",
                        workflow_hints=(),
                    )
                ]

                proposals = generate_proposals(sources, activities)

                self.assertEqual(proposals, [])


if __name__ == "__main__":
    unittest.main()
