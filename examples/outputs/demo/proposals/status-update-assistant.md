---
artifact_type: agent_proposal
version: 1
agent_slug: status-update-assistant
status: draft
readiness: reviewed_required
generated_at: 2026-06-23T03:25:43+00:00
---

# Agent Proposal: Status Update Assistant

## What This Agent Helps With
Collect approved work signals and draft status updates, stakeholder summaries, and weekly reports.

## Why It Might Help
The approved work context shows a recurring `status` pattern across 4 evidence records.

## Confidence
0.78

## Agent Opportunity Scorecard
Overall opportunity: 4/5

- Frequency: 3/5 based on 4 evidence records in the lookback window.
- Repeatability: 4/5 based on recurring work artifacts and workflow hints.
- Source quality: 5/5 based on approved, read-only source scores.
- Risk: low; recommended first version stays draft-only and human-reviewed.
- Expected first useful output: draft status updates.

## Primary Sources
`jira`, `teams`

## Evidence Notes
- 2026-06-14T18:22:00Z: updated ticket &#x27;Launch readiness tracker&#x27; - Updated blocker status and owner notes before weekly stakeholder recap. \(jira:LAUNCH-42\)
- 2026-06-15T16:45:00Z: commented thread &#x27;Launch follow-up&#x27; - Answered questions about blocker owners and next steps after the customer rollout sync. \(teams:thread_204\)
- 2026-06-18T21:10:00Z: reviewed ticket &#x27;Release blocker review&#x27; - Reviewed blocker tickets and grouped remaining risks for stakeholder status update. \(jira:LAUNCH-58\)
- 2026-06-19T13:20:00Z: commented thread &#x27;Weekly update inputs&#x27; - Collected status snippets from stakeholders and asked for missing owners before sending update. \(teams:thread_244\)

## Allowed Actions
- draft status updates
- summarize progress signals
- highlight blockers
- prepare stakeholder-ready reports

## Blocked Actions
- send messages or emails without human approval
- modify source systems
- evaluate employee performance
- make legal, medical, financial, HR, hiring, or eligibility decisions
- use unapproved sources

## Output Folders
- `Agent Work/status-update-assistant/config`
- `Agent Work/status-update-assistant/drafts`
- `Agent Work/status-update-assistant/reports`
- `Agent Work/status-update-assistant/archive`

## Invocation Examples
- Ask Status Update Assistant to prepare this week's draft.
- Ask Status Update Assistant to review approved context and list open loops.
- Ask Status Update Assistant to draft, but not send, a follow-up.

## Required User Confirmations
- Confirm this role matches a real pain point.
- Confirm the listed sources are approved for this agent.
- Confirm output folders and retention expectations.
- Confirm whether the agent may draft, summarize, classify, or only advise.

## Success Metrics
- User keeps or refines the proposal after review.
- Draft outputs require less editing over time.
- The agent reduces repeated manual preparation work.

## Next Step
Review this proposal, edit the boundaries, then generate or install the target-specific agent scaffold.
