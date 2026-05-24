# Contributing to PhishStrike

Thank you for helping improve PhishStrike. This project is intended for **authorized security education and penetration testing only**.

## Before you contribute

- Use PhishStrike only on systems and people who have given **written permission**
- Do not commit secrets (`.env`, API keys, `auth/*.db`, capture logs)
- Preserve GPL-3.0 attribution when modifying `.sites/` templates derived from [Zphisher](https://github.com/htr-tech/zphisher)

## Development setup

```bash
git clone https://github.com/farouqshaheen/PhishStrike.git
cd PhishStrike
pip install -r requirements-dev.txt
cp .env.example .env
# Edit .env — set SECRET_KEY and ADMIN_PASSWORD
python scripts/setup_admin.py
```

## Running tests

```bash
pytest tests/ -v
python test_phishstrike.py
python test_new_modules.py
```

## Code style

- Match existing module layout under `phishstrike/`, `lib/`, and `dashboard/`
- Keep changes focused; avoid unrelated refactors in the same PR
- Prefer `lib/logger.py` over silent `except` blocks

## Pull requests

1. Describe **what** changed and **why**
2. Note how you tested (commands + results)
3. Update `CHANGELOG.md` for user-visible changes

## Reporting issues

Use GitHub Issues with:

- OS and Python version
- Steps to reproduce
- Expected vs actual behavior
- Redacted logs (no real victim credentials)
