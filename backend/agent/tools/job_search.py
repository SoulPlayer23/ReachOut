import re

import httpx

# Job board domain → source_key
_DOMAIN_MAP = [
    ("linkedin.com", "linkedin"),
    ("indeed.com", "indeed"),
    ("naukri.com", "naukri"),
    ("glassdoor.com", "glassdoor"),
    ("wellfound.com", "wellfound"),
    ("careers.google.com", "google_jobs"),
    ("careers.", "google_jobs"),   # careers.company.com
]


def search_jobs(
    role: str,
    company: str,
    location: str,
    serper_key: str,
    enabled_sources: list[str],
) -> list[dict]:
    """
    Search for jobs via Serper.dev web search.
    Returns [{title, company, location, url, source}].
    """
    site_filters = _build_site_filters(enabled_sources)
    query = f'{role} {company} {location} jobs {site_filters}'.strip()

    try:
        r = httpx.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": serper_key, "Content-Type": "application/json"},
            json={"q": query, "num": 10, "gl": "in"},
            timeout=15,
        )
        r.raise_for_status()
        organic = r.json().get("organic", [])
    except Exception:
        return []

    results = []
    seen_urls: set[str] = set()

    for item in organic:
        url = item.get("link", "")
        title = item.get("title", "")
        snippet = item.get("snippet", "")

        if url in seen_urls:
            continue

        source = _detect_source(url)

        # Skip if this source is not enabled (unless google_jobs catchall)
        if source != "google_jobs" and source not in enabled_sources:
            continue

        # Skip non-job pages (reviews, profiles, etc.)
        if _is_non_job_page(url, title):
            continue

        parsed = _parse_job(title, snippet, company, location, url, source)
        if parsed:
            seen_urls.add(url)
            results.append(parsed)

    return results[:8]


def _build_site_filters(enabled_sources: list[str]) -> str:
    domain_map = {
        "linkedin": "site:linkedin.com/jobs",
        "indeed": "site:indeed.com",
        "naukri": "site:naukri.com",
        "glassdoor": "site:glassdoor.com",
        "wellfound": "site:wellfound.com",
    }
    sites = [domain_map[s] for s in enabled_sources if s in domain_map]
    if not sites:
        return ""
    if len(sites) == 1:
        return sites[0]
    return "(" + " OR ".join(sites) + ")"


def _detect_source(url: str) -> str:
    url_lower = url.lower()
    for needle, key in _DOMAIN_MAP:
        if needle in url_lower:
            return key
    return "google_jobs"


def _is_non_job_page(url: str, title: str) -> bool:
    skip_patterns = ["/reviews", "/profile", "/in/", "employee-reviews",
                     "salary", "interview", "working-at"]
    url_lower = url.lower()
    return any(p in url_lower for p in skip_patterns)


def _parse_job(title: str, snippet: str, company: str, location: str, url: str, source: str) -> dict | None:
    # Strip site-specific suffixes from title (e.g. "Software Engineer - Google | LinkedIn")
    clean_title = re.split(r"\s*[-|–]\s*(linkedin|indeed|naukri|glassdoor|google|wellfound)", title, flags=re.I)[0].strip()

    # Try to extract a specific role title from snippet if title is a listing page
    if any(w in clean_title.lower() for w in ["jobs in", "job vacancies", "job openings", "1,000+", "200 "]):
        # Extract first role from snippet
        lines = snippet.split("·")
        if len(lines) > 1:
            clean_title = lines[1].strip()
        else:
            return None  # Skip aggregate listing pages

    if not clean_title:
        return None

    return {
        "title": clean_title,
        "company": company,
        "location": location,
        "url": url,
        "source": source,
    }
