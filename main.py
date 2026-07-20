"""Entry point: fetch jobs from all sources, filter, dedupe against seen_jobs.json,
email new matches, and update seen_jobs.json."""
import json
import os
import yaml

from ats_sources import fetch_all as fetch_ats_jobs
from internshala_source import fetch_internshala
from filters import is_relevant
from notifier import send_email

SEEN_JOBS_PATH = "seen_jobs.json"


def load_seen() -> set:
    if not os.path.exists(SEEN_JOBS_PATH):
        return set()
    with open(SEEN_JOBS_PATH, "r") as f:
        return set(json.load(f))


def save_seen(seen: set):
    with open(SEEN_JOBS_PATH, "w") as f:
        json.dump(sorted(seen), f, indent=2)


def load_companies() -> list[dict]:
    with open("companies.yaml", "r") as f:
        data = yaml.safe_load(f)
    return data.get("companies", [])


def main():
    is_first_run = not os.path.exists(SEEN_JOBS_PATH)
    seen = load_seen()

    companies = load_companies()
    ats_jobs = fetch_ats_jobs(companies)
    internshala_jobs = fetch_internshala()
    all_jobs = ats_jobs + internshala_jobs
    print(f"Fetched {len(all_jobs)} total postings ({len(ats_jobs)} ATS, {len(internshala_jobs)} Internshala)")

    if is_first_run:
        # Bootstrap: record everything currently listed as "already seen" so the
        # first run doesn't email you every open role at once. You'll only get
        # alerted about postings that appear AFTER this first run.
        for job in all_jobs:
            seen.add(f"{job['source']}:{job['id']}")
        save_seen(seen)
        print(f"First run: seeded {len(seen)} existing postings as seen, no email sent this time.")
        return

    new_matches = []
    for job in all_jobs:
        uid = f"{job['source']}:{job['id']}"
        if uid in seen:
            continue
        seen.add(uid)

        if is_relevant(job["title"], job.get("location", ""), job.get("description", "")):
            new_matches.append(job)

    print(f"{len(new_matches)} new job(s) matched your filters")
    for j in new_matches:
        print(f"  - [{j['source']}] {j['title']} ({j.get('company', '')})")

    send_email(new_matches)
    save_seen(seen)


if __name__ == "__main__":
    main()
