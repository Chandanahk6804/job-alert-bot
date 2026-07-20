"""Scrape Internshala's fresher-jobs listing pages.

Internshala doesn't have a public API, so this parses their server-rendered
HTML. These pages ARE server-rendered (not client-side JS-only), so plain
requests + BeautifulSoup works without a headless browser.

NOTE: This is HTML scraping, which is inherently more fragile than an API.
If Internshala changes their page markup, this will need updating — that's
expected maintenance, not a bug. The selectors below are intentionally loose
(built around the /job/detail/ URL pattern rather than CSS classes) to
survive minor styling changes.
"""
import re
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
}

# Category listing pages covering the roles Chandana wants, fresher-filtered.
LISTING_URLS = [
    "https://internshala.com/fresher-jobs/software-development-jobs/",
    "https://internshala.com/fresher-jobs/web-development-jobs/",
    "https://internshala.com/fresher-jobs/full-stack-development-jobs/",
]


def _extract_jobs_from_page(html: str, source_url: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    jobs = []
    seen_ids = set()

    for link in soup.find_all("a", href=re.compile(r"/job/detail/")):
        href = link.get("href", "")
        title = link.get_text(strip=True)
        if not title or href in seen_ids:
            continue
        seen_ids.add(href)

        # Walk up to a container with enough surrounding text to pull
        # company/location/description out of.
        container = link
        for _ in range(6):
            if container.parent is None:
                break
            container = container.parent
            if len(container.get_text(strip=True)) > 200:
                break

        full_text = container.get_text(" ", strip=True)
        url = href if href.startswith("http") else f"https://internshala.com{href}"

        # Job id from the URL's trailing digits, used for dedup.
        id_match = re.search(r"(\d+)$", href.rstrip("/"))
        job_id = id_match.group(1) if id_match else href

        jobs.append({
            "source": "internshala",
            "id": job_id,
            "title": title,
            "location": full_text,  # location is embedded in the text blob; filters.py checks substrings
            "url": url,
            "description": full_text,
            "company": "",  # not cleanly separable without brittle class selectors; title/url are enough to identify
        })
    return jobs


def fetch_internshala() -> list[dict]:
    all_jobs = []
    for url in LISTING_URLS:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=20)
            if resp.status_code != 200:
                print(f"[internshala] {url} -> HTTP {resp.status_code}, skipping")
                continue
            jobs = _extract_jobs_from_page(resp.text, url)
            all_jobs.extend(jobs)
        except Exception as e:
            print(f"[internshala] Error fetching {url}: {e}")
    # De-dupe across the multiple listing pages (a job can appear in more than one category)
    unique = {}
    for j in all_jobs:
        unique[j["id"]] = j
    return list(unique.values())
