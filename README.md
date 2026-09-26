# Hatekhori (হাতে খড়ি)

Turns a person's own handwriting into a real, installable font — Bengali
and Hindi first. See `docs/AGENTS.md` before touching anything; it is the
standing spec and wins over ad-hoc decisions.

## Status

Milestone 1 in progress: pipeline kill-test (English, private, never
shown publicly). See `docs/PRD.md` §9 for the definition of done.

## Local setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend is static for now — open `frontend/index.html` directly, or
serve it with any static file server.

## Docs

- `docs/AGENTS.md` — standing build rules, read this first
- `docs/PRD.md` — product requirements
- `docs/BRAND.md` — brand strategy and positioning
- `docs/privacy-policy.md` — on-site privacy policy source of truth
- `docs/hatekhori-brand-colors.md`, `docs/hatekhori-layout-grid.md` — visual system
