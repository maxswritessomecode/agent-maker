import unittest

from agent_maker.core import Source
from agent_maker.generator import Proposal
from agent_maker.render import render_proposal, render_source_report


class RenderTests(unittest.TestCase):
    def test_source_report_escapes_markdown_and_html(self):
        report = render_source_report([
            Source(
                source_id="docs",
                name="<img src=x onerror=alert(1)> | [open](file:///tmp/x)",
                category="docs",
                availability="connected",
                approved=True,
                read_only=True,
            )
        ])

        self.assertIn("&lt;img", report)
        self.assertIn("\\[open\\]", report)
        self.assertIn("\\|", report)

    def test_proposal_escapes_evidence_notes(self):
        proposal = Proposal(
            agent_slug="safe-agent",
            agent_name="Safe Agent",
            mission="Help safely.",
            pattern="status",
            confidence=0.8,
            opportunity_score=3,
            scorecard=("Frequency: 1/5 based on one record.",),
            risk_level="low",
            evidence_count=1,
            source_ids=("source`id",),
            evidence_notes=("<img src=x> [open](file:///tmp/x) ![remote](https://example.com/x.png)",),
            allowed_actions=("draft only",),
            blocked_actions=("send",),
            required_confirmations=("confirm",),
            output_dirs=("Agent Work/safe-agent/config",),
            success_metrics=("useful",),
        )

        rendered = render_proposal(proposal)

        self.assertIn("&lt;img", rendered)
        self.assertIn("\\[open\\]", rendered)
        self.assertIn("\\!\\[remote\\]", rendered)
        self.assertIn("`source'id`", rendered)
        self.assertIn("## Agent Opportunity Scorecard", rendered)
        self.assertIn("## Confidence Breakdown", rendered)
        self.assertIn("classified_as:", rendered)


if __name__ == "__main__":
    unittest.main()
