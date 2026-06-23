# Agent Proposal: Status Update Assistant

## What This Agent Helps With

Draft weekly stakeholder updates from approved project signals such as email updates, meeting notes, tickets, docs, and chat threads.

## Why It Might Help

- Observed pattern: the user repeatedly gathers blockers, owners, decisions, and next steps from several sources.
- Frequency or lookback window: 9 relevant records across the last 10 days.
- Why this is worth agentizing: the work is recurring, structured, and safe if kept draft-only.

## Agent Opportunity Scorecard

Overall opportunity: 5/5

- Frequency: 5/5 based on repeated weekly status artifacts.
- Repeatability: 4/5 because the output format is consistent: progress, blockers, decisions, owners, next steps.
- Source quality: 4/5 because approved sources have timestamps, authors, links, and stable IDs.
- Risk: low because the first version drafts only and never sends.
- Expected first useful output: a stakeholder-ready weekly update draft.

## Evidence

| Claim | Evidence | Confidence | Caveat |
|---|---|---:|---|
| Weekly updates are recurring | Outlook subjects, Jira status changes, and project doc edits from the last 10 days | High | User should confirm the cadence is representative |
| Updates require cross-source synthesis | Teams threads reference blockers that also appear in tickets and meeting notes | Medium | Some blockers may belong to other owners |
| Draft-only behavior is low risk | The output is a reviewable update, not an autonomous action | High | Agent must never publish or send without approval |

## Allowed Actions

- summarize approved project context
- group progress, blockers, decisions, and next steps
- draft stakeholder updates for review
- list missing evidence and questions

## Blocked Actions

- send or publish updates without human approval
- change tickets, docs, emails, or chat messages
- evaluate people or compare employee productivity
- make HR, legal, medical, financial, eligibility, or regulated decisions
- use unapproved sources

## Inputs

- Required approved sources: tickets, project docs, meeting notes
- Optional approved sources: email and chat metadata
- User prompts this agent expects: "draft weekly update," "summarize blockers," "prepare stakeholder recap"

## Outputs

- weekly update drafts
- blocker summaries
- decision and owner lists
- questions for missing context

## Output Folders

- `Agent Work/status-update-assistant/config`
- `Agent Work/status-update-assistant/drafts`
- `Agent Work/status-update-assistant/reports`
- `Agent Work/status-update-assistant/archive`

## Invocation Examples

- "Ask Status Update Assistant to draft this week's launch update."
- "Ask Status Update Assistant to summarize blockers from approved project context."
- "Ask Status Update Assistant to prepare a draft, but do not send or publish it."

## Required Confirmations

- Does this match a real weekly pain point?
- Are tickets, docs, meeting notes, email, and chat approved for this agent?
- Should the agent use a fixed update template?
- Where should drafts and reports be stored?

## Readiness

Draft. User review required before activation.

