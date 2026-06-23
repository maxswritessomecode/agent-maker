# Context Sources

Agent Maker can use any source already available and approved in the user's assistant environment. The source must be read-only for discovery.

## High-Signal Sources

| Source | Useful signals | Common agents |
|---|---|---|
| Email | requests, replies, commitments, updates | inbox triage, follow-up drafting |
| Calendar | recurring meetings, stakeholders, cadence | prep packets, follow-up coordinators |
| Meeting notes | action items, decisions, blockers | meeting summaries, open-loop tracking |
| Chat | quick decisions, unresolved asks, coordination | channel digests, stakeholder updates |
| Docs | drafts, decisions, requirements | decision memos, doc review assistants |
| Tickets | status, blockers, releases | status updates, release notes |
| GitHub/GitLab | PRs, issues, changelogs | release notes, review summaries |
| CRM/support | customer context, open issues | account briefings, response drafts |

## Source Usefulness Questions

- Is it approved for this user and this purpose?
- Is it read-only?
- Does it show the user's actual work?
- Can the user's work be distinguished from other people's work?
- Does it contain stable IDs, timestamps, authors, and links?
- Is the signal dense enough to justify token use?
- Could it contain sensitive or regulated content?

