import json

from agent.llm import chat
from agent.prompts import email_draft_prompt


def draft_email(
    user_name: str,
    target_role: str,
    company: str,
    recruiter_name: str | None,
    company_description: str,
    tone: str = "professional",
) -> dict:
    """
    Draft a cold email using the configured LLM.
    Returns {"subject": str, "body": str}.
    """
    prompt = email_draft_prompt(
        user_name=user_name,
        target_role=target_role,
        company=company,
        recruiter_name=recruiter_name,
        company_description=company_description,
        tone=tone,
    )

    response = chat(
        messages=[{"role": "user", "content": prompt}],
    )

    return _parse_response(response, target_role, company)


def _parse_response(text: str, role: str, company: str) -> dict:
    # Strip markdown code fences if present
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        cleaned = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

    try:
        data = json.loads(cleaned)
        return {
            "subject": str(data.get("subject", f"{role} opportunity at {company}")),
            "body": str(data.get("body", text)),
        }
    except (json.JSONDecodeError, ValueError):
        # LLM didn't return valid JSON — use full text as body
        return {
            "subject": f"{role} opportunity at {company}",
            "body": text,
        }
