from __future__ import annotations

import os
import re
import time
import html
import unicodedata
from dataclasses import dataclass, field
from typing import List, Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")

ROLE_PATTERNS = [
    r"\bAssistant Professor\b",
    r"\bAssociate Professor\b",
    r"\bDistinguished Professor\b",
    r"\bInstitute Professor\b",
    r"\bProfessor and Chair\b",
    r"\bProfessor\b",
    r"\bChair\b",
    r"\bDirector\b",
    r"\bDean\b",
    r"\bResearch Scientist\b",
    r"\bScientist\b",
    r"\bResearcher\b",
    r"\bEngineer\b",
    r"\bLecturer\b",
    r"\bPostdoctoral\b",
    r"\bPostdoc\b",
]

DEGREE_PATTERNS = [
    r"\bPh\.?\s?D\.?\b",
    r"\bEd\.?\s?D\.?\b",
    r"\bSc\.?\s?D\.?\b",
    r"\bD\.?\s?Phil\.?\b",
    r"\bM\.?\s?S\.?\b",
    r"\bM\.?\s?A\.?\b",
    r"\bB\.?\s?S\.?\b",
    r"\bB\.?\s?A\.?\b",
    r"\bBachelor(?:'s)?\b",
    r"\bMaster(?:'s)?\b",
    r"\bDoctorate\b",
]

AFFILIATION_HINTS = [
    "University", "College", "Institute", "School of", "Department of",
    "Laboratory", "Lab", "Center", "Centre", "Hospital", "Company", "Inc."
]

BAD_EMAIL_PREFIXES = ("noreply", "no-reply", "donotreply", "privacy", "support", "info@")


@dataclass
class SearchResult:
    title: str
    link: str
    snippet: str = ""


@dataclass
class PersonInfo:
    query_name: str
    hint: str = ""
    role: Optional[str] = None
    degree: Optional[str] = None
    current_affiliation: Optional[str] = None
    public_email: Optional[str] = None
    linkedin: Optional[str] = None
    image_url: Optional[str] = None
    sources: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def normalize_name(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return text.lower().strip()


def get_domain(url: str) -> str:
    try:
        return urlparse(url).netloc.lower()
    except Exception:
        return ""


def serpapi_google_search_raw(query: str, num: int = 10) -> dict:
    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        raise RuntimeError("Thiếu SERPAPI_KEY trong file .env")

    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google",
        "q": query,
        "api_key": api_key,
        "num": min(max(num, 1), 10),
        "hl": "en",
    }

    response = requests.get(url, params=params, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return response.json()


def search_web(query: str, num: int = 10) -> List[SearchResult]:
    data = serpapi_google_search_raw(query, num=num)

    results: List[SearchResult] = []
    for item in data.get("organic_results", []):
        results.append(
            SearchResult(
                title=item.get("title", "") or "",
                link=item.get("link", "") or "",
                snippet=item.get("snippet", "") or "",
            )
        )

    return results


def search_person_image(name: str, hint: str = "") -> Optional[str]:
    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        raise RuntimeError("Thiếu SERPAPI_KEY trong file .env")

    query = name
    if hint:
        query += f" {hint}"
    query += " headshot"

    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google_images",
        "q": query,
        "api_key": api_key,
        "hl": "en",
    }

    response = requests.get(url, params=params, headers=HEADERS, timeout=30)
    response.raise_for_status()
    data = response.json()

    image_results = data.get("images_results") or data.get("image_results") or []
    if not image_results:
        return None

    first = image_results[0]
    return first.get("original") or first.get("thumbnail")


def fetch_html(url: str) -> Optional[str]:
    try:
        response = requests.get(url, headers=HEADERS, timeout=20)
        response.raise_for_status()
        content_type = response.headers.get("Content-Type", "").lower()

        if "text/html" not in content_type:
            return None

        return response.text
    except Exception:
        return None


def html_to_text(html_content: str) -> str:
    soup = BeautifulSoup(html_content, "html.parser")

    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    text = html.unescape(text)

    lines = [normalize_space(line) for line in text.splitlines()]
    lines = [line for line in lines if line]
    return "\n".join(lines)


def score_result(result: SearchResult, name: str) -> int:
    score = 0
    url = result.link.lower()
    title = result.title.lower()
    snippet = result.snippet.lower()
    norm_name = normalize_name(name)

    if norm_name in normalize_name(title):
        score += 5
    if norm_name in normalize_name(snippet):
        score += 3

    if any(token in url for token in [".edu", ".ac.", "/faculty", "/profile", "/people", "/person", "/directory", "/team"]):
        score += 4

    if any(token in title for token in ["faculty", "profile", "directory", "department", "school", "lab"]):
        score += 3

    if "linkedin.com/in/" in url:
        score += 2

    if any(bad in url for bad in ["facebook.com", "instagram.com", "x.com", "twitter.com", "researchgate.net"]):
        score -= 2

    return score


def pick_best_results(results: List[SearchResult], name: str, max_items: int = 6) -> List[SearchResult]:
    unique = []
    seen = set()

    for item in results:
        if not item.link or item.link in seen:
            continue
        seen.add(item.link)
        unique.append(item)

    unique.sort(key=lambda item: score_result(item, name), reverse=True)
    return unique[:max_items]


def find_public_email(text: str) -> Optional[str]:
    emails = EMAIL_RE.findall(text)
    if not emails:
        return None

    filtered = []
    for email in emails:
        email_lower = email.lower()
        if any(email_lower.startswith(prefix) for prefix in BAD_EMAIL_PREFIXES):
            continue
        filtered.append(email)

    if not filtered:
        return None

    filtered.sort(key=lambda e: (
        0 if (".edu" in e or ".org" in e or ".gov" in e) else 1,
        len(e)
    ))
    return filtered[0]


def extract_degree(text: str) -> Optional[str]:
    lines = text.splitlines()
    candidates = []

    for line in lines[:400]:
        if len(line) > 250:
            continue
        if any(re.search(pattern, line, flags=re.IGNORECASE) for pattern in DEGREE_PATTERNS):
            candidates.append(line)

    if not candidates:
        return None

    candidates.sort(key=len)
    return candidates[0][:250]


def extract_role(text: str) -> Optional[str]:
    lines = text.splitlines()
    candidates = []

    for line in lines[:300]:
        if len(line) > 220:
            continue
        if any(re.search(pattern, line, flags=re.IGNORECASE) for pattern in ROLE_PATTERNS):
            candidates.append(line)

    if not candidates:
        return None

    candidates.sort(key=len)
    return candidates[0][:220]


def extract_affiliation(text: str) -> Optional[str]:
    lines = text.splitlines()
    candidates = []

    for line in lines[:350]:
        if len(line) > 220:
            continue
        if any(hint.lower() in line.lower() for hint in AFFILIATION_HINTS):
            candidates.append(line)

    if not candidates:
        return None

    candidates.sort(key=lambda x: (
        0 if ("University" in x or "Institute" in x or "College" in x) else 1,
        len(x)
    ))
    return candidates[0][:220]


def find_linkedin(results: List[SearchResult]) -> Optional[str]:
    for item in results:
        if "linkedin.com/in/" in item.link.lower():
            return item.link
    return None


def merge_field(current: Optional[str], new_value: Optional[str]) -> Optional[str]:
    return current if current else new_value


def enrich_from_page(info: PersonInfo, url: str, text: str) -> None:
    info.public_email = merge_field(info.public_email, find_public_email(text))
    info.degree = merge_field(info.degree, extract_degree(text))
    info.role = merge_field(info.role, extract_role(text))
    info.current_affiliation = merge_field(info.current_affiliation, extract_affiliation(text))

    if url not in info.sources:
        info.sources.append(url)


def query_templates(name: str, hint: str = "") -> List[str]:
    base = f"\"{name}\""
    if hint:
        base += f" \"{hint}\""

    return [
        f"{base} faculty profile",
        f"{base} university profile",
        f"{base} CV",
        f"{base} biography",
        f"{base} email",
        f"site:linkedin.com/in/ {base}",
    ]


def search_person(name: str, hint: str = "") -> PersonInfo:
    info = PersonInfo(query_name=name, hint=hint)
    all_results: List[SearchResult] = []

    raw_query = f"\"{name}\""
    if hint:
        raw_query += f" \"{hint}\""

    try:
        raw_data = serpapi_google_search_raw(raw_query, num=10)

        kg = raw_data.get("knowledge_graph", {})
        header_images = kg.get("header_images", [])
        if header_images:
            first_header = header_images[0]
            info.image_url = first_header.get("image") or first_header.get("thumbnail")

        if not info.image_url:
            for item in raw_data.get("organic_results", []):
                thumb = item.get("thumbnail")
                if thumb:
                    info.image_url = thumb
                    break
    except Exception as exc:
        info.notes.append(f"Image prefetch failed: {exc}")

    for query in query_templates(name, hint):
        try:
            results = search_web(query, num=10)
            all_results.extend(results)
            time.sleep(0.8)
        except Exception as exc:
            info.notes.append(f"Search failed for query '{query}': {exc}")

    if not all_results:
        if not info.image_url:
            try:
                info.image_url = search_person_image(name, hint)
            except Exception as exc:
                info.notes.append(f"Image search failed: {exc}")

        info.notes.append("Không có search result nào.")
        return info

    info.linkedin = find_linkedin(all_results)
    best_results = pick_best_results(all_results, name, max_items=6)

    for result in best_results:
        if "linkedin.com/" in result.link.lower():
            continue

        html_content = fetch_html(result.link)
        if not html_content:
            continue

        text = html_to_text(html_content)
        enrich_from_page(info, result.link, text)

    if not info.role or not info.current_affiliation or not info.degree:
        for result in best_results:
            snippet = result.snippet or ""
            if not info.role and any(re.search(p, snippet, flags=re.IGNORECASE) for p in ROLE_PATTERNS):
                info.role = snippet[:220]
            if not info.degree and any(re.search(p, snippet, flags=re.IGNORECASE) for p in DEGREE_PATTERNS):
                info.degree = snippet[:220]
            if not info.current_affiliation and any(h.lower() in snippet.lower() for h in AFFILIATION_HINTS):
                info.current_affiliation = snippet[:220]

    if not info.image_url:
        try:
            info.image_url = search_person_image(name, hint)
        except Exception as exc:
            info.notes.append(f"Image search failed: {exc}")

    return info


if __name__ == "__main__":
    targets = [
        {"name": "Miroslav Krstić", "hint": "UC San Diego"},
        {"name": "Zhong-Ping Jiang", "hint": "NYU"},
        {"name": "Wassim M. Haddad", "hint": "Georgia Tech"},
    ]

    for target in targets:
        result = search_person(target["name"], target.get("hint", ""))

        print("=" * 80)
        print("Name:", result.query_name)
        print("Hint:", result.hint)
        print("Role:", result.role or "Not found")
        print("Degree:", result.degree or "Not found")
        print("Current affiliation:", result.current_affiliation or "Not found")
        print("Public email:", result.public_email or "Not found")
        print("LinkedIn:", result.linkedin or "Not found")
        print("Image:", result.image_url or "Not found")
        print("Sources:")
        for src in result.sources:
            print(" -", src)
        if result.notes:
            print("Notes:")
            for note in result.notes:
                print(" -", note)
        print("=" * 80)