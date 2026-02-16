from __future__ import annotations

import json
from dataclasses import dataclass
from urllib.error import URLError
from urllib.request import urlopen

from multi_agents.agents.base import BaseAgent


GREENHOUSE_SOURCES = {
    "OpenAI": "https://boards-api.greenhouse.io/v1/boards/openai/jobs",
    "Anthropic": "https://boards-api.greenhouse.io/v1/boards/anthropic/jobs",
}


@dataclass(slots=True)
class JobListing:
    company: str
    title: str
    location: str
    absolute_url: str
    updated_at: str
    score: float


class JobHunterAgent(BaseAgent):
    name = "job_hunter"

    def fetch_jobs(self) -> list[dict]:
        jobs: list[dict] = []
        for company, url in GREENHOUSE_SOURCES.items():
            try:
                with urlopen(url, timeout=20) as response:  # nosec B310
                    payload = json.loads(response.read().decode("utf-8"))
            except (URLError, TimeoutError, json.JSONDecodeError, ValueError):
                continue

            for job in payload.get("jobs", []):
                jobs.append(
                    {
                        "company": company,
                        "title": job.get("title", "Unknown"),
                        "location": (job.get("location") or {}).get("name", "Unknown"),
                        "absolute_url": job.get("absolute_url", ""),
                        "updated_at": job.get("updated_at", ""),
                    }
                )
        return jobs

    @staticmethod
    def score_job(job: dict, query: str, location: str, profile: dict) -> float:
        haystack = " ".join(
            [
                str(job.get("title", "")).lower(),
                str(job.get("location", "")).lower(),
                str(query).lower(),
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

    def search(self, query: str, location: str, profile: dict, limit: int = 10) -> list[JobListing]:
        ranked = []
        for job in self.fetch_jobs():
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
        return ranked[:limit]
