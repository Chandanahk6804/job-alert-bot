"""Filtering logic: decide if a job posting matches what Chandana is looking for."""
import re

ROLE_KEYWORDS = [
    "software engineer", "software developer", "software development engineer",
    "development engineer", "sde", "sde-1", "sde 1", "sde1",
    "frontend", "front-end", "front end",
    "backend", "back-end", "back end",
    "full stack", "fullstack", "full-stack",
    "web developer", "web development", "application developer",
    "programmer", "developer",
]

FRESHER_KEYWORDS = [
    "fresher", "freshers", "entry level", "entry-level", "graduate",
    "trainee", "0-1 year", "0-2 year", "junior", "new grad", "campus",
    "associate software", "intern",
]

# Roles that match ROLE_KEYWORDS but are almost never a fit — filters out noise.
EXCLUDE_KEYWORDS = [
    "senior", "sr.", "staff", "principal", "lead ", "manager", "director",
    "architect", "vp ", "head of", "10+ years", "8+ years", "5+ years",
]

INDIA_LOCATION_HINTS = [
    "india", "bangalore", "bengaluru", "hyderabad", "mumbai", "pune",
    "chennai", "delhi", "gurgaon", "gurugram", "noida", "kolkata",
    "remote - india", "remote (india)",
]


def _contains_any(text: str, keywords: list[str]) -> bool:
    text = text.lower()
    return any(kw in text for kw in keywords)


def is_relevant(title: str, location: str, description: str = "") -> bool:
    """Return True if a job posting looks like a fresher SDE/frontend/backend/
    fullstack role based in India."""
    title_l = title.lower()
    combined = f"{title} {description}".lower()

    if _contains_any(title_l, EXCLUDE_KEYWORDS):
        return False

    role_match = _contains_any(title_l, ROLE_KEYWORDS)
    if not role_match:
        return False

    fresher_match = _contains_any(combined, FRESHER_KEYWORDS)
    if not fresher_match:
        return False

    location_match = _contains_any(location, INDIA_LOCATION_HINTS) or "india" in combined
    if not location_match:
        return False

    return True
