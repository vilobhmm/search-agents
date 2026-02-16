from __future__ import annotations

from dataclasses import asdict, dataclass

from multi_agents.agents.cc import Briefing, CCAgent
from multi_agents.agents.job_hunter import JobHunterAgent, JobListing


@dataclass(slots=True)
class TeamResult:
    jobs: list[JobListing]
    briefing: Briefing
    heartbeat: dict


class AgentTeam:
    def __init__(self) -> None:
        self.job_hunter = JobHunterAgent()
        self.cc = CCAgent()

    def run(self, query: str, location: str, profile: dict, limit: int = 10) -> TeamResult:
        jobs = self.job_hunter.search(query=query, location=location, profile=profile, limit=limit)
        briefing = self.cc.build_briefing(jobs=jobs, query=query, location=location)
        pulse = {
            "job_hunter": asdict(self.job_hunter.heartbeat(mode="monitoring")),
            "cc": asdict(self.cc.heartbeat(mode="coordinating")),
        }
        return TeamResult(jobs=jobs, briefing=briefing, heartbeat=pulse)
