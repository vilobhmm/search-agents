from __future__ import annotations

from dataclasses import asdict, dataclass

from multi_agents.agents.cc import Briefing, CCAgent
from multi_agents.agents.job_hunter import CompanySearchGuidance, JobHunterAgent, JobListing


@dataclass(slots=True)
class TeamResult:
    jobs: list[JobListing]
    briefing: Briefing
    heartbeat: dict
    guidance: list[CompanySearchGuidance]
    requested_companies: list[str]


class AgentTeam:
    def __init__(self) -> None:
        self.job_hunter = JobHunterAgent()
        self.cc = CCAgent()

    def run(
        self,
        query: str,
        location: str,
        profile: dict,
        companies: list[str] | None = None,
        limit: int = 10,
    ) -> TeamResult:
        search_response = self.job_hunter.search(
            query=query,
            location=location,
            profile=profile,
            companies=companies,
            limit=limit,
        )
        briefing = self.cc.build_briefing(
            jobs=search_response.jobs,
            query=query,
            location=location,
            guidance=search_response.guidance,
        )
        pulse = {
            "job_hunter": asdict(self.job_hunter.heartbeat(mode="monitoring")),
            "cc": asdict(self.cc.heartbeat(mode="coordinating")),
        }
        return TeamResult(
            jobs=search_response.jobs,
            briefing=briefing,
            heartbeat=pulse,
            guidance=search_response.guidance,
            requested_companies=search_response.requested_companies,
        )
