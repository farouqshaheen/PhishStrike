# Changelog

All notable changes to PhishStrike are documented here.

## [3.0.0] — 2026-05-23

### Added
- Modular `phishstrike/` package (CLI, capture, server, tunnel, features)
- Dashboard login with Flask-Login, bcrypt, and `scripts/setup_admin.py`
- Internal `/api/internal/refresh` for CLI → dashboard live updates
- Optional Fernet encryption for captured passwords (`CAPTURE_ENCRYPT=true`)
- CSRF protection and login rate limiting on the dashboard
- Configurable data retention (`RETENTION_DAYS`)
- Pytest suite and GitHub Actions CI workflow
- `CONTRIBUTING.md`, expanded security documentation

### Changed
- `phishstrike.py` is now a thin launcher (`python -m phishstrike` supported)
- Default dashboard bind address: `127.0.0.1` (local-only)
- Default SocketIO runtime for live WebSocket updates
- README credits Zphisher template lineage (GPL-3.0)

### Security
- Removed default weak admin password auto-creation
- `.gitignore` covers `ai_output/`, `auth/ai_config.json`, and capture artifacts

## [2.x] — Earlier releases

- Flask dashboard with Excel/CSV/PDF export
- Gemini AI assistant, 30+ templates, Cloudflared & LocalXpose tunnels
- Cyber terminal UI and Docker support
