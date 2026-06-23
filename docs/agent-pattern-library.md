# Agent Pattern Library

This library translates common public agent examples into the work signals Agent Maker should look for. It is designed for non-technical users first: every pattern starts with sources they already recognize.

## Research Snapshot

Public agent ecosystems cluster around a few repeatable patterns:

- Skill ecosystems emphasize reusable folders of instructions, scripts, and resources for specialized work. GitHub's Copilot docs and Anthropic's skills repo both describe skills this way.
- No-code agent marketplaces emphasize business templates: lead enrichment, sales prep, inbox handling, support triage, content creation, project updates, and CRM work.
- Automation template repositories expose the practical source systems behind those agents: Gmail/Outlook, Slack/Teams, calendars, CRM, support desks, tickets, Google Drive, GitHub, and docs.

Sources reviewed:

- GitHub Awesome Copilot: https://github.com/github/awesome-copilot
- GitHub custom agents docs: https://docs.github.com/en/copilot/reference/custom-agents-configuration
- Anthropic Skills repo: https://github.com/anthropics/skills
- Zapier agent templates: https://zapier.com/templates/agents
- Gumloop templates: https://www.gumloop.com/templates
- n8n template collection: https://github.com/enescingoz/awesome-n8n-templates
- Lindy AI agent use cases: https://www.lindy.ai/blog/ai-agent-use-cases
- Relevance AI marketplace: https://marketplace.relevanceai.com/

## Best Mass-Market Agent Candidates

| Agent candidate | Who benefits | Source signals to detect | First safe output | Keep draft-only? |
|---|---|---|---|---|
| Inbox Triage Partner | founders, operators, managers, support, sales | repeated email threads, labels, reply drafts, unresolved asks, sender groups | daily inbox brief and reply drafts | yes |
| Meeting Follow-up Coordinator | almost every knowledge worker | recurring meetings, notes, action items, follow-up emails, Teams/Slack threads | follow-up draft and open-loop list | yes |
| Status Update Assistant | PMs, leads, consultants, chiefs of staff | weekly update emails, tickets, docs, chat snippets, calendar cadence | weekly stakeholder update draft | yes |
| Account Briefing Assistant | sales, customer success, founders | CRM records, sales emails, call notes, company research, support history | account or call prep brief | yes |
| Support Triage Assistant | support, success, IT, operations | support emails, Zendesk/Jira tickets, escalations, customer sentiment, Slack handoffs | ticket summary and draft response | yes |
| Release Notes Assistant | engineering-adjacent leads, PMs, QA | PRs, commits, issues, tickets, changelog docs, release meetings | audience-specific release notes draft | yes |
| Content Repurposing Assistant | marketers, founders, creators, consultants | blogs, transcripts, docs, webinars, newsletters, social drafts | LinkedIn/X/newsletter drafts | yes |
| Research Briefing Assistant | strategy, sales, PMs, analysts | saved links, research docs, competitor notes, news trackers, call prep docs | sourced research brief | yes |
| Project Intake Assistant | ops, PMs, team leads | Slack/Teams requests, Asana/Jira/Linear tasks, docs, intake forms | draft task/project brief | yes |
| Knowledge Base Q&A Assistant | support, IT, ops, onboarding | docs, policy pages, FAQs, resolved tickets, help center articles | answer draft with source links | yes |
| Expense/Invoice Admin Assistant | operations, finance-adjacent users | receipts, invoice PDFs, email attachments, sheets | categorized expense report | yes, with stricter review |
| Calendar Focus Planner | managers, ICs, founders | calendar density, meeting topics, recurring commitments, Slack mentions | focus block recommendations | yes |

## Patterns To Block Or Treat As Sensitive

Public marketplaces often include HR and regulated examples. Agent Maker should not recommend these by default, even if they are popular elsewhere.

Blocked:

- resume screening
- candidate ranking
- interview debrief collection
- employee satisfaction analysis
- performance review or calibration
- compensation, promotion, or termination decisions
- customer eligibility or regulated decisions
- legal, medical, or financial advice

Safer substitute:

- HR policy Q&A from approved policy docs can be allowed only as informational drafting, never as employee evaluation or decision support.

## Reverse-Engineering Source Signals

When a user says "find agent ideas," infer likely candidates from repeated signals:

| Repeated signal | Likely agent |
|---|---|
| "Can you send a recap?" after meetings | Meeting Follow-up Coordinator |
| weekly "status", "update", "blockers", or "next steps" artifacts | Status Update Assistant |
| repeated reply drafts, labels, unanswered asks | Inbox Triage Partner |
| CRM/account pages opened before calls | Account Briefing Assistant |
| support escalations plus draft replies | Support Triage Assistant |
| PRs/issues grouped around a release date | Release Notes Assistant |
| one source rewritten into many channels | Content Repurposing Assistant |
| saved links and competitor/company notes before decisions | Research Briefing Assistant |
| Slack/Teams asks converted into tickets | Project Intake Assistant |

## Ranking Heuristic

Prefer agents where:

- the same pattern appears at least 3 times in 7-14 days
- the first useful output is a draft, summary, brief, checklist, or report
- the source data is already approved and read-only
- the agent can succeed with metadata plus short excerpts
- the user can easily review the result
- the workflow avoids sensitive judgment and autonomous actions

