# Pattern Library

Use this when the user asks for examples, asks what agents are common, or provides broad context without a clear target agent.

## Common High-Value Candidates

| Candidate | Signals | First safe output |
|---|---|---|
| Inbox Triage Partner | email labels, reply drafts, unresolved asks, repeated senders | daily inbox brief and draft replies |
| Meeting Follow-up Coordinator | meeting notes, action items, follow-up emails, chat threads | follow-up draft and open-loop list |
| Status Update Assistant | weekly updates, tickets, docs, blockers, stakeholder threads | weekly update draft |
| Account Briefing Assistant | CRM records, sales emails, call notes, company research | account or call prep brief |
| Support Triage Assistant | support tickets, escalations, sentiment, customer emails | ticket summary and draft response |
| Release Notes Assistant | PRs, commits, issues, tickets, changelog docs | release notes draft |
| Content Repurposing Assistant | blogs, transcripts, docs, webinars, social drafts | platform-specific content drafts |
| Research Briefing Assistant | saved links, research docs, news, competitor notes | sourced research brief |
| Project Intake Assistant | Slack/Teams requests, tickets, docs, intake forms | draft task or project brief |
| Knowledge Base Q&A Assistant | docs, FAQs, resolved tickets, policy pages | answer draft with source links |
| Calendar Focus Planner | calendar density, recurring meetings, mentions | focus block recommendations |

## Blocked Or Sensitive Public Patterns

Do not recommend these even if they appear in public agent marketplaces:

- resume screening
- candidate ranking
- interview debrief collection
- employee satisfaction analysis
- performance review or calibration
- compensation, promotion, or termination decisions
- customer eligibility or regulated decisions
- legal, medical, or financial advice

For HR policy Q&A, only suggest informational drafting from approved policy docs. Never evaluate people.

## Signal Mapping

- Email + repeated replies -> Inbox Triage Partner
- Meeting notes + follow-up language -> Meeting Follow-up Coordinator
- Tickets + weekly updates + blockers -> Status Update Assistant
- CRM + call notes + company research -> Account Briefing Assistant
- Support tickets + escalations -> Support Triage Assistant
- PRs/issues + release language -> Release Notes Assistant
- Blog/transcript/docs + social/newsletter drafts -> Content Repurposing Assistant
- Research links + competitor/company notes -> Research Briefing Assistant

