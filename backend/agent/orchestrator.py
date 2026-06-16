import json
import re
from dataclasses import dataclass, field
from typing import Generator

from sqlalchemy.orm import Session as DBSession

from agent.llm import chat
from agent.tools.company_info import get_company_info
from agent.tools.email_draft import draft_email
from agent.tools.email_send import send_email
from agent.tools.job_search import search_jobs
from agent.tools.recruiter import find_recruiters
from config import settings
from crypto import decrypt
from models import ApiKeys, Preferences, Source, User

# ── In-memory session store (user_id → Session) ───────────────────────────────
_sessions: dict[int, "_Session"] = {}


@dataclass
class _Session:
    state: str = "IDLE"
    intent: dict = field(default_factory=dict)   # {company, role, location}
    jobs: list = field(default_factory=list)
    selected_job: dict | None = None
    recruiters: list = field(default_factory=list)
    selected_recruiter: dict | None = None
    company_info: dict | None = None
    email_draft: dict | None = None              # {subject, body}


# ── SSE helpers ───────────────────────────────────────────────────────────────

def _event(type: str, **data) -> str:
    return f"data: {json.dumps({'type': type, **data})}\n\n"


def _text(content: str) -> str:
    return _event("text", content=content)


# ── Main entry point ──────────────────────────────────────────────────────────

def run_stream(
    message: str,
    user: User,
    db: DBSession,
) -> Generator[str, None, None]:
    """Sync generator — yields SSE event strings for the chat router."""
    session = _sessions.setdefault(user.id, _Session())
    keys = _load_keys(db, user.id)
    prefs = _load_prefs(db, user.id)

    try:
        yield from _dispatch(message, user, session, keys, prefs, db)
    except Exception as e:
        yield _event("error", message=str(e))


# ── State dispatcher ──────────────────────────────────────────────────────────

def _dispatch(
    message: str,
    user: User,
    session: _Session,
    keys: dict,
    prefs: dict,
    db: DBSession,
) -> Generator[str, None, None]:

    # Allow "reset" or "start over" from any state
    if re.search(r"\b(reset|start over|new email|restart)\b", message, re.I):
        _sessions[user.id] = _Session()
        session = _sessions[user.id]
        yield _text("Sure, let's start fresh. Which company and role are you targeting?")
        return

    if session.state in ("IDLE", "GATHER_INTENT"):
        yield from _handle_gather_intent(message, user, session, keys, prefs, db)

    elif session.state == "SELECT_JOB":
        yield from _handle_select_job(message, user, session, keys, prefs, db)

    elif session.state == "SELECT_RECRUITER":
        yield from _handle_select_recruiter(message, user, session, keys, prefs, db)

    elif session.state == "REVIEW_EMAIL":
        yield from _handle_review_email(message, user, session, keys, prefs, db)

    else:
        session.state = "IDLE"
        yield _text("Let's start over. Which company and role are you targeting?")


# ── Stage handlers ────────────────────────────────────────────────────────────

def _handle_gather_intent(message, user, session, keys, prefs, db):
    yield _text("Let me figure out what you're looking for…")

    intent = _extract_intent(message, prefs)
    session.intent.update({k: v for k, v in intent.items() if v})

    missing = [f for f in ("role", "company") if not session.intent.get(f)]
    if missing:
        session.state = "GATHER_INTENT"
        questions = {"role": "What role are you applying for?", "company": "Which company?"}
        yield _text(" ".join(questions[f] for f in missing))
        return

    if not session.intent.get("location"):
        session.intent["location"] = prefs.get("default_location") or "India"

    yield from _run_job_search(user, session, keys, prefs, db)


def _handle_select_job(message, user, session, keys, prefs, db):
    idx = _parse_selection(message, len(session.jobs))
    if idx is None:
        yield _text(f"Please pick a job — reply with a number between 1 and {len(session.jobs)}.")
        return

    session.selected_job = session.jobs[idx]
    job = session.selected_job
    yield _text(f"Got it — **{job['title']}** at **{job['company']}**. Finding recruiters…")

    yield from _run_recruiter_search(user, session, keys, prefs, db)


def _handle_select_recruiter(message, user, session, keys, prefs, db):
    idx = _parse_selection(message, len(session.recruiters))
    if idx is None:
        yield _text(f"Please pick a recruiter — reply with a number between 1 and {len(session.recruiters)}.")
        return

    session.selected_recruiter = session.recruiters[idx]
    rec = session.selected_recruiter
    yield _text(f"Using **{rec['name'] or rec['email']}**. Drafting your email…")

    yield from _run_draft_email(user, session, keys, prefs, db)


def _handle_review_email(message, user, session, keys, prefs, db):
    if _is_approval(message):
        yield from _run_send_email(user, session, keys, prefs, db)
        return

    # User provided edits — update the draft body and re-show
    if len(message.strip()) > 20:
        session.email_draft["body"] = message.strip()
        yield _text("Updated your email. Does this look good?")
        yield _event(
            "email_preview",
            subject=session.email_draft["subject"],
            body=session.email_draft["body"],
        )
        yield _text('Reply **"send"** to send, or paste a revised version.')
    else:
        yield _text('Reply **"send"** or **"approve"** to send the email, or paste your edits.')


# ── Job search flow ───────────────────────────────────────────────────────────

def _run_job_search(user, session, keys, prefs, db):
    intent = session.intent
    serper_key = keys.get("serper") or settings.serper_api_key
    if not serper_key:
        yield _text("⚠ No Serper API key configured. Add it in Settings → Connections.")
        return

    enabled_sources = _enabled_job_boards(db, user.id)
    yield _text(f"Searching for **{intent['role']}** roles at **{intent['company']}** in {intent['location']}…")

    jobs = search_jobs(
        role=intent["role"],
        company=intent["company"],
        location=intent["location"],
        serper_key=serper_key,
        enabled_sources=enabled_sources,
    )

    if not jobs:
        yield _text("No job listings found. Try a broader search — reply with a different role or company.")
        session.state = "GATHER_INTENT"
        session.intent = {}
        return

    session.jobs = jobs
    session.state = "SELECT_JOB"
    yield _event("jobs", items=jobs)
    yield _text(f"Found {len(jobs)} opening(s). Reply with the number of the role you want to target.")


# ── Recruiter search flow ─────────────────────────────────────────────────────

def _run_recruiter_search(user, session, keys, prefs, db):
    job = session.selected_job
    domain = _extract_domain(job.get("url", ""), job.get("company", ""))

    enabled_recruiters = _enabled_recruiters(db, user.id)
    recruiters = find_recruiters(
        company_domain=domain,
        enabled_sources=enabled_recruiters,
        apollo_key=keys.get("apollo") or settings.apollo_api_key or None,
        hunter_key=keys.get("hunter") or settings.hunter_api_key or None,
    )

    # Get company info silently in parallel logic (sequential here for simplicity)
    serper_key = keys.get("serper") or settings.serper_api_key
    if serper_key:
        session.company_info = get_company_info(job["company"], serper_key)

    if not recruiters:
        yield _text(
            "No recruiter contacts found via Apollo/Hunter. "
            "You can paste a recruiter's email directly and I'll draft the email for them."
        )
        session.state = "GATHER_INTENT"
        return

    session.recruiters = recruiters
    session.state = "SELECT_RECRUITER"
    yield _event("recruiters", items=recruiters)
    yield _text(f"Found {len(recruiters)} recruiter(s). Reply with the number to target.")


# ── Email draft flow ──────────────────────────────────────────────────────────

def _run_draft_email(user, session, keys, prefs, db):
    job = session.selected_job
    rec = session.selected_recruiter
    company_desc = (session.company_info or {}).get("description", f"{job['company']} is a company.")

    draft = draft_email(
        user_name=user.name,
        target_role=job["title"],
        company=job["company"],
        recruiter_name=rec.get("name") or None,
        company_description=company_desc,
        tone=prefs.get("tone", "professional"),
    )

    session.email_draft = draft
    session.state = "REVIEW_EMAIL"

    yield _event("email_preview", subject=draft["subject"], body=draft["body"])
    yield _text('Here\'s your draft. Reply **"send"** to send it, or paste your edits.')


# ── Send flow ─────────────────────────────────────────────────────────────────

def _run_send_email(user, session, keys, prefs, db):
    job = session.selected_job
    rec = session.selected_recruiter
    draft = session.email_draft

    yield _text(f"Sending to **{rec['email']}**…")
    try:
        result = send_email(
            db=db,
            user=user,
            to_email=rec["email"],
            subject=draft["subject"],
            body=draft["body"],
            company=job["company"],
            role=job["title"],
            recruiter_name=rec.get("name"),
        )
        yield _event("sent", message_id=result["message_id"])
        yield _text(f"✓ Email sent to {rec['email']}! Good luck with your application.")
    except Exception as e:
        yield _event("error", message=f"Failed to send email: {e}")
    finally:
        _sessions[user.id] = _Session()


# ── Helper utilities ──────────────────────────────────────────────────────────

def _extract_intent(message: str, prefs: dict) -> dict:
    """Use LLM to extract company, role, location from a natural language message."""
    default_location = prefs.get("default_location") or "India"
    target_roles = prefs.get("target_roles") or []
    roles_hint = f"User's common roles: {', '.join(target_roles)}." if target_roles else ""

    prompt = f"""{roles_hint}
Extract the job search intent from this message: "{message}"

Return JSON only, no explanation:
{{
  "company": "company name or null",
  "role": "job title or null",
  "location": "location or null (default: {default_location})"
}}"""

    try:
        raw = chat([{"role": "user", "content": prompt}])
        cleaned = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        data = json.loads(cleaned)
        return {
            "company": data.get("company") or None,
            "role": data.get("role") or None,
            "location": data.get("location") or None,
        }
    except Exception:
        return {"company": None, "role": None, "location": None}


def _parse_selection(message: str, count: int) -> int | None:
    """Parse a user's item selection ('1', 'first', 'the second one', etc.) → 0-based index."""
    words = {"first": 0, "second": 1, "third": 2, "fourth": 3, "fifth": 4,
             "1st": 0, "2nd": 1, "3rd": 2, "4th": 3, "5th": 4}
    msg = message.strip().lower()

    for word, idx in words.items():
        if word in msg and idx < count:
            return idx

    m = re.search(r"\b([1-9]\d*)\b", msg)
    if m:
        idx = int(m.group(1)) - 1
        if 0 <= idx < count:
            return idx

    return None


def _is_approval(message: str) -> bool:
    keywords = ["approve", "send", "send it", "yes", "ok", "okay",
                "looks good", "go ahead", "perfect", "great", "do it"]
    msg = message.strip().lower()
    return any(k in msg for k in keywords)


def _extract_domain(url: str, company: str) -> str:
    """Extract company domain from job URL, or fall back to a name-based guess."""
    if url:
        m = re.search(r"https?://(?:www\.)?([^/]+)", url)
        if m:
            host = m.group(1)
            # Skip job board domains
            boards = {"linkedin.com", "indeed.com", "glassdoor.com",
                      "naukri.com", "wellfound.com", "google.com"}
            if not any(b in host for b in boards):
                return host
    # Fallback: company_name.com
    slug = re.sub(r"[^a-z0-9]", "", company.lower())
    return f"{slug}.com"


def _load_keys(db: DBSession, user_id: int) -> dict:
    row = db.query(ApiKeys).filter(ApiKeys.user_id == user_id).first()
    if not row:
        return {}
    result = {}
    if row.serper_key_enc:
        result["serper"] = decrypt(row.serper_key_enc)
    if row.apollo_key_enc:
        result["apollo"] = decrypt(row.apollo_key_enc)
    if row.hunter_key_enc:
        result["hunter"] = decrypt(row.hunter_key_enc)
    if row.ollama_api_key_enc:
        result["ollama"] = decrypt(row.ollama_api_key_enc)
    return result


def _load_prefs(db: DBSession, user_id: int) -> dict:
    row = db.query(Preferences).filter(Preferences.user_id == user_id).first()
    if not row:
        return {}
    return {
        "default_location": row.default_location,
        "target_roles": row.target_roles or [],
        "tone": row.tone or "professional",
    }


def _enabled_job_boards(db: DBSession, user_id: int) -> list[str]:
    rows = db.query(Source).filter(
        Source.user_id == user_id,
        Source.category == "job_board",
        Source.enabled == True,  # noqa: E712
    ).all()
    return [r.source_key for r in rows]


def _enabled_recruiters(db: DBSession, user_id: int) -> list[str]:
    rows = db.query(Source).filter(
        Source.user_id == user_id,
        Source.category == "recruiter",
        Source.enabled == True,  # noqa: E712
    ).all()
    return [r.source_key for r in rows]
