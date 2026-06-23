# Contributing

Agent Maker needs real-world workflow examples more than clever abstractions.

## Useful Contributions

- anonymized source metadata examples
- sample agent proposals for specific roles
- safer blocked-domain rules
- runtime renderers for Codex, Claude, Copilot, Zapier, Gumloop, or n8n
- improvements to no-Python skill instructions
- UX feedback from non-technical users

## Safety Rules

- Do not commit private emails, chats, documents, tickets, customer names, credentials, or secrets.
- Use anonymized examples.
- Keep generated agents draft-only unless a human approval gate is explicit.
- Do not add HR, performance-review, legal, medical, financial-advice, customer-eligibility, regulated-decision, or employee-monitoring workflows.

## Testing

Run:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Validate the skill:

```bash
UV_PROJECT_ENVIRONMENT=/tmp/agent-maker-skill-validate uv run --no-project --with pyyaml python ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/agent-maker
```

The `UV_PROJECT_ENVIRONMENT` and `--no-project` flags keep validation from creating `.venv` or `uv.lock` in this repo.
