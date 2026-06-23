---
artifact_type: agent_proposal
version: 1
agent_slug: inbox-triage-partner
status: draft
readiness: reviewed_required
generated_at: 2026-06-23T03:25:43+00:00
---

# Agent Proposal: Inbox Triage Partner

## What This Agent Helps With
Help prioritize routine work email, draft responses, and surface unresolved commitments.

## Why It Might Help
The approved work context shows a recurring `email` pattern across 2 evidence records.

## Confidence
0.70

## Agent Opportunity Scorecard
Overall opportunity: 3/5

- Frequency: 2/5 based on 2 evidence records in the lookback window.
- Repeatability: 5/5 based on recurring work artifacts and workflow hints.
- Source quality: 5/5 based on approved, read-only source scores.
- Risk: medium; recommended first version stays draft-only and human-reviewed.
- Expected first useful output: classify approved email threads.

## Primary Sources
`outlook`

## Evidence Notes
- 2026-06-13T15:10:00Z: sent email &#x27;Weekly launch status&#x27; - Sent launch status update with progress, blockers, next steps, and owners. \(outlook:msg_1001\)
- 2026-06-20T15:25:00Z: sent email &#x27;Weekly launch status&#x27; - Sent another weekly update with progress, blockers, decisions, owners, and next steps. \(outlook:msg_1122\)

## Allowed Actions
- classify approved email threads
- draft replies for review
- summarize unresolved threads
- prepare daily inbox briefs

## Blocked Actions
- send messages or emails without human approval
- modify source systems
- evaluate employee performance
- make legal, medical, financial, HR, hiring, or eligibility decisions
- use unapproved sources

## Output Folders
- `Agent Work/inbox-triage-partner/config`
- `Agent Work/inbox-triage-partner/drafts`
- `Agent Work/inbox-triage-partner/reports`
- `Agent Work/inbox-triage-partner/archive`

## Invocation Examples
- Ask Inbox Triage Partner to prepare this week's draft.
- Ask Inbox Triage Partner to review approved context and list open loops.
- Ask Inbox Triage Partner to draft, but not send, a follow-up.

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
