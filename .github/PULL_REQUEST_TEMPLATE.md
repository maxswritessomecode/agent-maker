## Summary

## Safety checklist

- [ ] No private source data, credentials, secrets, or customer data included
- [ ] No HR, hiring, performance review, legal, medical, financial-advice, customer-eligibility, regulated-decision, or employee-monitoring workflow added
- [ ] New examples are anonymized or synthetic
- [ ] Tests updated when behavior changes

## Test command

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests -v
UV_PROJECT_ENVIRONMENT=/tmp/agent-maker-skill-validate uv run --no-project --with pyyaml python ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/agent-maker
```
