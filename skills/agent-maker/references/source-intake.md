# Source Intake

Use this checklist when the user has not provided a source manifest.

## Low-Friction Prompt

Ask:

> Which approved work context should I use: email, calendar, meetings, chat, docs, tickets, code, CRM/support, or local exports? Also choose a lookback window: 7, 10, 14, or 30 days.

## Recommended Defaults

- Individual productivity: 10 days
- Project/team coordination: 14 days
- Monthly reporting or strategic work: 30 days
- High-token environments: start with 7 days and expand only if needed

## Source Suitability Table

| Source | Usually Good For | Common Risks |
|---|---|---|
| Email | triage, follow-ups, recurring replies, commitments | private content, customers, legal/finance |
| Calendar | meeting prep, weekly patterns, coordination load | thin context without notes |
| Meeting notes/transcripts | action items, decisions, follow-up agents | third-party/coworker sensitive data |
| Slack/Teams | open loops, stakeholder updates, channel summaries | noise, prompt injection, cross-user profiling |
| Docs/Drive/Confluence | decision memos, project briefs, research synthesis | confidential strategy, stale docs |
| Tickets/Jira/Linear | status updates, blockers, release notes | incomplete context, team-process assumptions |
| Code/GitHub | PR summaries, changelogs, release prep | repo permissions, secret leakage |
| CRM/support | account briefs, response drafting | regulated/customer eligibility decisions |

## Minimal Evidence Rules

- Prefer source locators, titles, dates, and short redacted notes.
- Avoid pasting full private messages.
- Keep evidence tied to the user's own work, not coworker profiling.
- Label claims as observed, inferred, or user-provided.
