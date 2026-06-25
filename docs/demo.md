# Demo Walkthrough

This walkthrough shows the no-Python product loop.

## 1. Start With A Bounded Prompt

```text
Use $agent-maker to look at the work I did over the last 10 days. Use email, calendar, meeting notes, Teams or Slack, docs, and tickets only if already approved. Start metadata-first and recommend 1-3 draft-only agents that could help.
```

## 2. Source Inventory

Agent Maker should first report what it can inspect and whether each source is useful:

| Source | Usefulness | Reason |
|---|---:|---|
| Outlook email | High | repeated status updates and follow-ups |
| Calendar + meeting notes | High | action items and decisions |
| Teams | Medium | useful open-loop context, noisy threads |
| HR drive | Excluded | regulated or sensitive source |

## 3. Ranked Recommendations

```text
1. Status Update Assistant
   Why: repeated weekly updates across email, docs, tickets, and chat
   Opportunity: 5/5
   Risk: low, draft-only

2. Meeting Follow-up Coordinator
   Why: recurring meeting notes create follow-ups and open loops
   Opportunity: 4/5
   Risk: low, human review required
```

## 4. Proposal Review

The user reviews:

- evidence
- confidence
- source list
- allowed actions
- blocked actions
- output folders
- required confirmations

## 5. Scaffold Spec

Only after approval:

```text
Generate a scaffold spec for Status Update Assistant. Keep raw content out of memory, require human review, and include eval cases.
```
