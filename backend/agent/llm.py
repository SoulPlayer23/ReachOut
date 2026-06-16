import httpx
from config import settings


def chat(messages: list[dict], system: str = "") -> str:
    """
    Send a chat completion request to the configured LLM provider.
    Returns the assistant's reply as a plain string.
    """
    provider = settings.llm_provider

    if provider == "claude":
        return _claude(messages, system)
    elif provider == "openai":
        return _openai_compat(
            messages, system,
            base_url=settings.openai_base_url or "https://api.openai.com/v1",
            api_key=settings.openai_api_key,
            model=settings.openai_model,
        )
    else:  # ollama (default)
        return _openai_compat(
            messages, system,
            base_url=settings.ollama_base_url.rstrip("/") + "/v1",
            api_key=settings.ollama_api_key or "ollama",
            model=settings.ollama_model,
        )


def _openai_compat(messages: list[dict], system: str, base_url: str, api_key: str, model: str) -> str:
    payload: dict = {"model": model, "messages": messages}
    if system:
        payload["messages"] = [{"role": "system", "content": system}] + messages

    r = httpx.post(
        f"{base_url}/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json=payload,
        timeout=60,
        follow_redirects=True,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip()


def _claude(messages: list[dict], system: str) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=system or anthropic.NOT_GIVEN,
        messages=messages,
    )
    return response.content[0].text.strip()
