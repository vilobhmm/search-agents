from dataclasses import asdict

from multi_agents.agents.job_hunter import CompanySearchGuidance, JobListing
from multi_agents.team import AgentTeam


class FakeTeam(AgentTeam):
    def __init__(self):
        super().__init__()

    def run(self, query: str, location: str, profile: dict, companies=None, limit: int = 10):
        jobs = [
            JobListing(
                company="OpenAI",
                title="Research Engineer",
                location="Remote",
                absolute_url="https://example.com",
                updated_at="2026-01-01",
                score=7.1,
            )
        ]
        guidance = [
            CompanySearchGuidance(
                company="Accenture",
                official_careers_url="https://www.accenture.com/in-en/careers/jobsearch",
                note="Direct API adapter not configured yet; use this official careers link.",
            )
        ]
        briefing = self.cc.build_briefing(jobs=jobs, query=query, location=location, guidance=guidance)
        pulse = {
            "job_hunter": asdict(self.job_hunter.heartbeat(mode="monitoring")),
            "cc": asdict(self.cc.heartbeat(mode="coordinating")),
        }
        return type(
            "Result",
            (),
            {
                "jobs": jobs,
                "briefing": briefing,
                "heartbeat": pulse,
                "guidance": guidance,
                "requested_companies": ["accenture"],
            },
        )


def test_team_briefing_has_content():
    team = FakeTeam()
    result = team.run(query="llm", location="", profile={})
    assert result.briefing.headline
    assert result.briefing.opportunities
    assert result.heartbeat["cc"]["mode"] == "coordinating"
    assert result.guidance[0].company == "Accenture"
