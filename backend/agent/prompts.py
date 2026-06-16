AGENT_SYSTEM = """You are ReachOut, an AI assistant that helps job seekers send personalized cold emails to recruiters.

You help the user through these steps:
1. Clarify their target company, role, and location
2. Search for matching job openings
3. Find recruiter contact details at the company
4. Draft a personalized cold email
5. Get the user's approval before sending

Be concise, helpful, and professional. Ask for only the information you actually need."""


def email_draft_prompt(
    user_name: str,
    target_role: str,
    company: str,
    recruiter_name: str | None,
    company_description: str,
    tone: str,
) -> str:
    greeting = f"Dear {recruiter_name}" if recruiter_name else "Dear Hiring Team"
    tone_instruction = {
        "professional": "formal and polished, suitable for a corporate environment",
        "casual": "friendly and approachable while remaining respectful",
        "enthusiastic": "energetic and passionate, showing genuine excitement about the opportunity",
    }.get(tone, "professional")

    return f"""Write a cold email from {user_name} to a recruiter at {company} for a {target_role} position.

Company context: {company_description}

Requirements:
- Tone: {tone_instruction}
- Greeting: {greeting}
- Length: 3 short paragraphs maximum
- Mention the specific role ({target_role}) and company ({company}) naturally
- Include a clear call to action (request a brief call or meeting)
- Do NOT include a subject line in the body
- Sign off with the sender's name: {user_name}

Return your response as JSON with exactly two keys:
{{
  "subject": "the email subject line",
  "body": "the full email body"
}}"""
