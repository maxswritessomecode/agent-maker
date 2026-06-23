# Runtime Targets

Use this when the user approves a proposal and asks to build or hand off an agent for a specific runtime.

## Codex Skill

Best for reusable assistant behavior inside Codex.

Generate:

- `SKILL.md` with concise trigger description
- optional `references/` templates
- allowed sources and blocked actions
- invocation examples
- output folder policy

## Claude Skill

Best for a packaged skill folder with instructions and resources.

Generate:

- skill folder outline
- `SKILL.md`
- reference files for templates, boundaries, and examples
- eval prompts for draft-only and blocked-domain behavior

## GitHub Copilot Custom Agent

Best for codebase or repository-oriented assistants.

Generate:

- custom agent instructions
- repository scope
- allowed read-only sources
- blocked write actions unless explicitly approved
- PR or issue output templates

## Zapier, Gumloop, n8n, Or Other Workflow Tools

Best when the workflow has known triggers and actions.

Generate:

- trigger candidates
- read-only data dependencies
- draft output step
- human approval step
- explicit blocked autonomous actions

Do not convert a proposal into an autonomous workflow unless the user explicitly asks for action permissions after reviewing the risks.
