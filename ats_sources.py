"""Fetch job postings from public ATS APIs (Greenhouse, Lever). No auth needed."""
import requests

HEADERS = {"User-Agent": "job-alert-bot/1.0 (personal job search tool)"}


def fetch_greenhouse(token: str) -> list[dict]:
    """Returns a list of normalized job dicts from a Greenhouse job board."""
    url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true"
    resp = requests.get(url, headers=HEADERS, timeout=20)
    if resp.status_code != 200:
        print(f"[greenhouse:{token}] HTTP {resp.status_code}, skipping")
        return []
    data = resp.json()
    jobs = []
    for j in data.get("jobs", []):
        jobs.append({
            "source": f"greenhouse:{token}",
            "id": str(j.get("id")),
            "title": j.get("title", ""),
            "location": (j.get("location") or {}).get("name", ""),
            "url": j.get("absolute_url", ""),
            "description": j.get("content", "") or "",
            "updated_at": j.get("updated_at", ""),
        })
    return jobs


def fetch_lever(token: str) -> list[dict]:
    """Returns a list of normalized job dicts from a Lever job board."""
    url = f"https://api.lever.co/v0/postings/{token}?mode=json"
    resp = requests.get(url, headers=HEADERS, timeout=20)
    if resp.status_code != 200:
        print(f"[lever:{token}] HTTP {resp.status_code}, skipping")
        return []
    data = resp.json()
    jobs = []
    for j in data:
        categories = j.get("categories", {}) or {}
        jobs.append({
            "source": f"lever:{token}",
            "id": str(j.get("id")),
            "title": j.get("text", ""),
            "location": categories.get("location", ""),
            "url": j.get("hostedUrl", ""),
            "description": j.get("descriptionPlain", "") or "",
            "updated_at": str(j.get("createdAt", "")),
        })
    return jobs


FETCHERS = {
    "greenhouse": fetch_greenhouse,
    "lever": fetch_lever,
}


def fetch_all(companies: list[dict]) -> list[dict]:
    all_jobs = []
    for company in companies:
        ats = company["ats"]
        token = company["token"]
        fetcher = FETCHERS.get(ats)
        if not fetcher:
            print(f"Unknown ATS type '{ats}' for {company.get('name')}, skipping")
            continue
        try:
            jobs = fetcher(token)
            for j in jobs:
                j["company"] = company.get("name", token)
            all_jobs.extend(jobs)
        except Exception as e:
            print(f"Error fetching {company.get('name')} ({ats}): {e}")
    return all_jobs
