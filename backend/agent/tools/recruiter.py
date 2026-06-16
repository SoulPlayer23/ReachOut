import httpx

_RECRUITER_TITLES = [
    "recruiter",
    "talent acquisition",
    "talent partner",
    "hr manager",
    "human resources",
    "people operations",
    "hiring manager",
]


def find_recruiters(
    company_domain: str,
    enabled_sources: list[str],
    apollo_key: str | None = None,
    hunter_key: str | None = None,
) -> list[dict]:
    """
    Discover recruiter contacts at a company.
    Returns [{name, title, email, source, confidence}].
    """
    results: list[dict] = []

    if "apollo" in enabled_sources and apollo_key:
        results.extend(_apollo_search(company_domain, apollo_key))

    if "hunter" in enabled_sources and hunter_key:
        results.extend(_hunter_search(company_domain, hunter_key))

    return _deduplicate(results)


def _apollo_search(domain: str, api_key: str) -> list[dict]:
    try:
        r = httpx.post(
            "https://api.apollo.io/v1/mixed_people/search",
            headers={"Content-Type": "application/json", "Cache-Control": "no-cache"},
            json={
                "api_key": api_key,
                "q_organization_domains": [domain],
                "person_titles": _RECRUITER_TITLES,
                "per_page": 10,
            },
            timeout=15,
        )
        r.raise_for_status()
        people = r.json().get("people", [])
    except Exception:
        return []

    results = []
    for p in people:
        email = p.get("email")
        if not email:
            continue
        results.append({
            "name": p.get("name", ""),
            "title": p.get("title", ""),
            "email": email,
            "source": "apollo",
            "confidence": 90,
        })
    return results


def _hunter_search(domain: str, api_key: str) -> list[dict]:
    try:
        r = httpx.get(
            "https://api.hunter.io/v2/domain-search",
            params={"domain": domain, "api_key": api_key, "type": "personal", "limit": 10},
            timeout=15,
        )
        r.raise_for_status()
        emails = r.json().get("data", {}).get("emails", [])
    except Exception:
        return []

    results = []
    for e in emails:
        position = (e.get("position") or "").lower()
        if not any(t in position for t in _RECRUITER_TITLES):
            continue
        name_parts = [e.get("first_name") or "", e.get("last_name") or ""]
        results.append({
            "name": " ".join(p for p in name_parts if p).strip(),
            "title": e.get("position", ""),
            "email": e.get("value", ""),
            "source": "hunter",
            "confidence": e.get("confidence", 0),
        })
    return results


def _deduplicate(contacts: list[dict]) -> list[dict]:
    seen: set[str] = set()
    unique = []
    for c in contacts:
        email = c["email"].lower()
        if email and email not in seen:
            seen.add(email)
            unique.append(c)
    return unique
