from __future__ import annotations

import json
import re
from dataclasses import dataclass
from urllib.error import URLError
from urllib.request import urlopen

from multi_agents.agents.base import BaseAgent

# Companies that currently have direct board API adapters in this project.
SUPPORTED_GREENHOUSE_BOARDS = {
    "openai": {"display_name": "OpenAI", "board_token": "openai"},
    "anthropic": {"display_name": "Anthropic", "board_token": "anthropic"},
}

# Official careers pages for requested companies. If direct API adapters are missing,
# we still return official search links (non-cached) so users can apply from source.
OFFICIAL_CAREER_SITES = {
    "accenture": "https://www.accenture.com/in-en/careers/jobsearch",
    "cognizant": "https://careers.cognizant.com/global/en",
    "infosys": "https://career.infosys.com/",
    "tcs": "https://www.tcs.com/careers",
    "tech mahindra": "https://careers.techmahindra.com/",
    "google": "https://www.google.com/about/careers/applications/jobs/results",
    "yahoo": "https://www.yahooinc.com/careers",
    "meta": "https://www.metacareers.com/jobs",
    "cisco": "https://jobs.cisco.com/jobs/SearchJobs/",
    "dell": "https://jobs.dell.com/",
    "cohesity": "https://www.cohesity.com/company/careers/",
    "openai": "https://openai.com/careers/",
    "anthropic": "https://www.anthropic.com/careers",
}


@dataclass(slots=True)
class JobListing:
    company: str
    title: str
    location: str
    absolute_url: str
    updated_at: str
    score: float


@dataclass(slots=True)
class CompanySearchGuidance:
    company: str
    official_careers_url: str
    note: str


@dataclass(slots=True)
class JobSearchResponse:
    jobs: list[JobListing]
    guidance: list[CompanySearchGuidance]
    requested_companies: list[str]


def _normalize_company_name(name: str) -> str:
    return re.sub(r"\s+", " ", name.strip().lower())


def extract_companies_from_query(query: str) -> list[str]:
    # supports inputs like: "... from accenture, cognizant, infosys"
    match = re.search(r"\bfrom\b\s+(.+)$", query, flags=re.IGNORECASE)
    if not match:
        return []

    chunk = match.group(1)
    companies = []
    for part in re.split(r",|\band\b", chunk, flags=re.IGNORECASE):
        cleaned = _normalize_company_name(part)
        if cleaned:
            companies.append(cleaned)

    deduped = list(dict.fromkeys(companies))
    return deduped


class JobHunterAgent(BaseAgent):
    name = "job_hunter"

    def _fetch_greenhouse_jobs(self, board_token: str, company_display_name: str) -> list[dict]:
        jobs: list[dict] = []
        url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs"
        try:
            with urlopen(url, timeout=20) as response:  # nosec B310
                payload = json.loads(response.read().decode("utf-8"))
        except (URLError, TimeoutError, json.JSONDecodeError, ValueError):
            return jobs

        for job in payload.get("jobs", []):
            jobs.append(
                {
                    "company": company_display_name,
                    "title": job.get("title", "Unknown"),
                    "location": (job.get("location") or {}).get("name", "Unknown"),
                    "absolute_url": job.get("absolute_url", ""),
                    "updated_at": job.get("updated_at", ""),
                }
            )
        return jobs

    def fetch_jobs(self, requested_companies: list[str]) -> tuple[list[dict], list[CompanySearchGuidance]]:
        jobs: list[dict] = []
        guidance: list[CompanySearchGuidance] = []

        # If user does not request specific companies, use all supported API sources.
        if not requested_companies:
            requested_companies = list(SUPPORTED_GREENHOUSE_BOARDS.keys())

        for company_key in requested_companies:
            board = SUPPORTED_GREENHOUSE_BOARDS.get(company_key)
            if board:
                jobs.extend(
                    self._fetch_greenhouse_jobs(
                        board_token=board["board_token"],
                        company_display_name=board["display_name"],
                    )
                )
                continue

            official_url = OFFICIAL_CAREER_SITES.get(company_key, "")
            if official_url:
                guidance.append(
                    CompanySearchGuidance(
                        company=company_key.title(),
                        official_careers_url=official_url,
                        note="Direct API adapter not configured yet; use this official careers link.",
                    )
                )
            else:
                guidance.append(
                    CompanySearchGuidance(
                        company=company_key.title(),
                        official_careers_url="",
                        note="No adapter or official careers URL found in registry.",
                    )
                )

        return jobs, guidance

    @staticmethod
    def score_job(job: dict, query: str, location: str, profile: dict) -> float:
        haystack = " ".join(
            [
                str(job.get("title", "")).lower(),
                str(job.get("location", "")).lower(),
                str(query).lower(),
                str(job.get("company", "")).lower(),
            ]
        )
        score = 0.0

        for token in str(query).lower().split():
            if token and token in haystack:
                score += 1.0

        if location and location.lower() in str(job.get("location", "")).lower():
            score += 2.5

        for skill in profile.get("skills", []):
            if str(skill).lower() in haystack:
                score += 1.2

        for target in profile.get("target_roles", []):
            if str(target).lower() in haystack:
                score += 1.0

        for pref in profile.get("preferred_locations", []):
            if str(pref).lower() in str(job.get("location", "")).lower():
                score += 0.8

        return round(score, 2)

    def search(
        self,
        query: str,
        location: str,
        profile: dict,
        companies: list[str] | None = None,
        limit: int = 10,
    ) -> JobSearchResponse:
        query_companies = extract_companies_from_query(query)
        requested_companies = [
            _normalize_company_name(c)
            for c in (companies or query_companies)
            if _normalize_company_name(c)
        ]

        jobs_raw, guidance = self.fetch_jobs(requested_companies=requested_companies)

        ranked = []
        for job in jobs_raw:
            score = self.score_job(job, query=query, location=location, profile=profile)
            ranked.append(
                JobListing(
                    company=job["company"],
                    title=job["title"],
                    location=job["location"],
                    absolute_url=job["absolute_url"],
                    updated_at=job["updated_at"],
                    score=score,
                )
            )

        ranked.sort(key=lambda x: x.score, reverse=True)
        return JobSearchResponse(
            jobs=ranked[:limit],
            guidance=guidance,
            requested_companies=requested_companies,
        )
