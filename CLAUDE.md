# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

ReachOut is a self-hosted cold email agent for job seekers. Users have a conversational chat interface where they describe a target company/role, the agent searches job boards and finds recruiter emails, drafts a personalized email via LLM, gets user approval, then sends it via Gmail with their resume attached.

## Running the application

Node is not installed on this machine. All frontend operations must be done via Docker:

```bash
# Start the app (Ollama Cloud mode — default)
docker compose up -d

# Start with local Ollama inference
docker compose --profile local up -d

# Rebuild after code changes
docker compose build && docker compose up -d

# View logs
docker compose logs -f app
docker compose logs -f db

# Run a frontend build to check for errors
docker run --rm -v $(pwd)/frontend:/app -w /app node:20-alpine npm run build

# Run frontend lint
docker run --rm -v $(pwd)/frontend:/app -w /app node:20-alpine npm run lint

# Open a Python shell inside the app container
docker compose exec app python
```

The app runs on **port 9000** (`http://localhost:9000`). Health check: `GET /health`.

## Docker build context

The Dockerfile lives at `backend/Dockerfile` but the **build context is the project root** (set in `docker-compose.yml`). This means paths inside the Dockerfile are relative to the repo root, not `backend/`. The multi-stage build compiles the React frontend in a `node:20-alpine` stage, then copies `frontend/dist` into the Python image at `backend/static/`.

FastAPI serves the built React files via `StaticFiles` — there is no Nginx container.

## Backend

- Entry point: `backend/main.py` — FastAPI app, `/health` route, static file serving
- All settings come from `backend/config.py` (Pydantic `BaseSettings` reading `.env`)
- `backend/db.py` — SQLAlchemy engine + `get_db()` dependency, `Base` for all models
- All new routers go in `backend/routers/`, imported and registered in `main.py`
- All agent tools go in `backend/agent/tools/`
- Use `settings` from `config.py` everywhere — never read `os.environ` directly

## Frontend

- Vite + React 19 + TypeScript, TailwindCSS v4 (via `@tailwindcss/vite` plugin — no `tailwind.config.js`)
- `src/index.css` contains only `@import "tailwindcss"` — do not add a separate PostCSS config
- `src/lib/api.ts` — pre-configured axios instance that injects the JWT from `localStorage`
- Dev proxy in `vite.config.ts` forwards `/api` and `/health` to `localhost:8000` (backend dev port)
- Route guards (`PrivateRoute`) check `localStorage.getItem('token')` — JWT stored as plain string

## LLM provider switching

The LLM provider is controlled entirely by `LLM_PROVIDER` in `.env`. The orchestrator (once built at `backend/agent/orchestrator.py`) must read `settings.llm_provider` and return the appropriate client — no provider logic should leak into tool files. Supported values: `ollama`, `claude`, `openai`.

When `LLM_PROVIDER=ollama` and running locally, `OLLAMA_BASE_URL` should be `http://ollama:11434` (Docker service name). For Ollama Cloud it is `https://api.ollama.com`.

## Resume access

The user's resume is mounted read-only from `~/.reachout/` on the host into `/app/userdata/` in the container. `settings.resume_path` gives the full container path. Never write to this directory.

## Key constraints

- `OVERVIEW.md` and `TODO.md` are gitignored — they are development references, not shipped
- All Docker container names are prefixed `reachout-` and volumes prefixed `reachout_` to avoid conflicts with other projects on the same machine
- Sensitive keys stored in the DB must be encrypted — use the `cryptography` library (already in `requirements.txt`)
- The `vite.config.ts` proxy targets port `8000` (the uvicorn port inside the container / local dev port). The host-exposed port is `9000` and is only relevant for Docker — don't confuse the two
