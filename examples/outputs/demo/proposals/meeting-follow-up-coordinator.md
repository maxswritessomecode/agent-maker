---
artifact_type: agent_proposal
version: 1
agent_slug: meeting-follow-up-coordinator
status: draft
readiness: reviewed_required
generated_at: 2026-06-25T12:40:13+00:00
---

# Agent Proposal: Meeting Follow-up Coordinator

## What This Agent Helps With
Turn approved meeting context into follow-up drafts, open-loop lists, and weekly meeting summaries.

## Why It Might Help
The user's recent work shows a recurring `meeting` pattern across 4 evidence records.

## Confidence
0.78

## Confidence Breakdown
- Avg activity confidence: 0.82 from source metadata.
- Evidence count weight: 0.78 from 4 record\(s\).
- Source quality: 1.00 average approved-source score.

## Agent Opportunity Scorecard
Overall opportunity: 4/5

- Frequency: 3/5 based on 4 evidence records in the lookback window.
  - 4 activity record\(s\) matched this pattern.
- Repeatability: 5/5 based on recurring work artifacts and workflow hints.
  - 4 of 4 activities share workflow_hint: &quot;meeting&quot;
  - 3 of 4 share object_type: &quot;meeting&quot;
  - Recurring title: &quot;customer rollout sync&quot; appeared 2x
- Source quality: 5/5 based on approved, read-only source scores.
  - outlook: primary \(1.00\)
  - calendar_notes: primary \(1.00\)
- Risk: 5/5 low; recommended first version stays draft-only and human-reviewed.
  - pattern=&quot;meeting&quot; starts draft-only and human-reviewed.
- Expected first useful output: summarize approved meeting notes.

## Primary Sources
`calendar_notes`, `outlook`

## Evidence Notes
- 2026-06-15T14:00:00Z: met meeting &#x27;Customer rollout sync&#x27; - Meeting notes include open action items, owners, decisions, and follow-up draft language. \(calendar:event_77\)
  - classified_as: meeting
  - signals: workflow_hint=&quot;meeting&quot;, text_match=&quot;meeting&quot;, object_type=&quot;meeting&quot;
- 2026-06-16T12:05:00Z: drafted email &#x27;Partner follow-up draft&#x27; - Drafted a follow-up message summarizing decisions, owners, and dates from meeting notes. \(outlook:draft_884\)
  - classified_as: meeting
  - signals: workflow_hint=&quot;meeting&quot;, text_match=&quot;meeting&quot;
- 2026-06-17T19:30:00Z: met meeting &#x27;Launch risks review&#x27; - Meeting notes record risk decisions, owner commitments, and unresolved questions for next update. \(calendar:event_91\)
  - classified_as: meeting
  - signals: workflow_hint=&quot;meeting&quot;, text_match=&quot;meeting&quot;, object_type=&quot;meeting&quot;
- 2026-06-21T17:00:00Z: met meeting &#x27;Customer rollout sync&#x27; - Recurring meeting notes include action item follow-ups and unresolved questions for next week. \(calendar:event_104\)
  - classified_as: meeting
  - signals: workflow_hint=&quot;meeting&quot;, text_match=&quot;meeting&quot;, object_type=&quot;meeting&quot;

## Allowed Actions
- summarize approved meeting notes
- extract likely action items
- draft follow-up messages
- maintain open-loop reports

## Blocked Actions
- send messages or emails without human approval
- modify source systems
- evaluate employee performance
- make legal, medical, financial, HR, hiring, or eligibility decisions
- use unapproved sources

## Output Folders
- `Agent Work/meeting-follow-up-coordinator/config`
- `Agent Work/meeting-follow-up-coordinator/drafts`
- `Agent Work/meeting-follow-up-coordinator/reports`
- `Agent Work/meeting-follow-up-coordinator/archive`

## Invocation Examples
- Ask Meeting Follow-up Coordinator to prepare this week's draft.
- Ask Meeting Follow-up Coordinator to review approved context and list open loops.
- Ask Meeting Follow-up Coordinator to draft, but not send, a follow-up.

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
