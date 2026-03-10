# ReachOut

A self-hosted web application that helps job seekers send personalized cold emails to recruiters.

ReachOut combines job discovery, recruiter finding, and AI-drafted email generation into a single conversational interface. The user approves each step — job selection, recruiter selection, email review — before anything is sent.

---

## How It Works

1. Tell the agent what role and company you're targeting
2. It searches enabled job boards and shows matching openings
3. It finds recruiters at that company via Apollo.io and Hunter.io
4. It drafts a personalized cold email using a local or cloud LLM
5. You review and approve the draft
6. It sends the email with your resume attached via Gmail

---

## Stack

- **Frontend** — React + Vite (TypeScript), TailwindCSS, shadcn/ui
- **Backend** — FastAPI (Python), SQLAlchemy, Alembic
- **Database** — PostgreSQL
- **LLM** — Ollama Cloud (default), swappable to local Ollama, Claude, or Groq via `.env`
- **Job Search** — Serper.dev (Google Jobs)
- **Recruiter Finding** — Apollo.io + Hunter.io
- **Email** — Gmail API (OAuth2)

---

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) + Docker Compose
- A Google Cloud project with the Gmail API enabled ([setup guide](docs/gmail-setup.md))
- API keys for: [Serper.dev](https://serper.dev), [Apollo.io](https://apollo.io), [Hunter.io](https://hunter.io)
- An [Ollama Cloud](https://ollama.com) account (or your own API key of choice)

---

## Quick Start

```bash
git clone https://github.com/SoulPlayer23/ReachOut.git
cd ReachOut

# Place your resume in the config directory
mkdir -p ~/.reachout
cp /path/to/your/resume.pdf ~/.reachout/resume.pdf

# Configure environment
cp .env.example .env
# Edit .env and fill in your API keys

# Start the application
docker compose up -d

# Open in browser
open http://localhost:8000
```

On first run, visit `/register` to create your account, then follow the onboarding steps to connect Gmail and configure your API keys.

---

## Configuration

All configuration is done via `.env`. Copy `.env.example` and fill in:

| Variable | Description |
|---|---|
| `SECRET_KEY` | Random string for JWT signing |
| `OLLAMA_API_KEY` | Ollama Cloud API key |
| `SERPER_API_KEY` | Serper.dev API key (job search) |
| `APOLLO_API_KEY` | Apollo.io API key (recruiter finding) |
| `HUNTER_API_KEY` | Hunter.io API key (recruiter finding) |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID (Gmail sending) |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret |

See `.env.example` for the full list and `OVERVIEW.md` for architecture details.

---

## License

MIT
