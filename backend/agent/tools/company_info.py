import httpx


def get_company_info(company: str, serper_key: str) -> dict:
    """
    Fetch a brief company summary via Serper.dev web search.
    Returns {description, industry, size_hint}.
    """
    try:
        r = httpx.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": serper_key, "Content-Type": "application/json"},
            json={"q": f"{company} company overview", "num": 5},
            timeout=15,
        )
        r.raise_for_status()
        data = r.json()
    except Exception:
        return _empty(company)

    # Prefer knowledge graph description if available
    kg = data.get("knowledgeGraph", {})
    description = kg.get("description", "")
    industry = kg.get("type", "")

    # Fall back to first organic snippet
    if not description:
        organics = data.get("organic", [])
        description = organics[0].get("snippet", "") if organics else ""

    # Try to infer size from snippet keywords
    size_hint = _infer_size(description)

    return {
        "description": description or f"{company} is a company.",
        "industry": industry,
        "size_hint": size_hint,
    }


def _infer_size(text: str) -> str:
    text = text.lower()
    if any(w in text for w in ["fortune 500", "multinational", "global leader", "worldwide"]):
        return "large"
    if any(w in text for w in ["startup", "early-stage", "seed", "series a", "founded in 202"]):
        return "startup"
    if any(w in text for w in ["mid-size", "mid-market", "growing"]):
        return "mid-size"
    return "unknown"


def _empty(company: str) -> dict:
    return {"description": f"{company} is a company.", "industry": "", "size_hint": "unknown"}
