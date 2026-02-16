from __future__ import annotations

from dataclasses import dataclass

from multi_agents.agents.base import BaseAgent
from multi_agents.agents.job_hunter import JobListing


@dataclass(slots=True)
class Briefing:
    headline: str
    priorities: list[str]
    opportunities: list[str]
    next_steps: list[str]


class CCAgent(BaseAgent):
    name = "cc"

    def build_briefing(self, jobs: list[JobListing], query: str, location: str) -> Briefing:
        top = jobs[:5]
        opportunities = [
            f"{idx + 1}. {j.title} @ {j.company} ({j.location}) [score={j.score}]"
            for idx, j in enumerate(top)
        ]

        priorities = [
            f"Refine search for: '{query}' in '{location or 'any location'}'.",
            "Prioritize applications with score >= 4.0.",
            "Track deadlines and submit high-fit applications first.",
        ]

        next_steps = [
            "Open top 3 links and tailor resume bullets to role language.",
            "Draft outreach note for one hiring manager/recruiter.",
            "Schedule follow-up reminders for pending applications.",
        ]

        return Briefing(
            headline="Daily multi-agent briefing ready.",
            priorities=priorities,
            opportunities=opportunities,
            next_steps=next_steps,
        )
