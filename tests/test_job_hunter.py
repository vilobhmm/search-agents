from multi_agents.agents.job_hunter import JobHunterAgent


def test_score_job_rewards_query_and_location():
    job = {
        "title": "Senior LLM Engineer",
        "location": "Remote - US",
    }
    profile = {
        "skills": ["python", "llm"],
        "target_roles": ["engineer"],
        "preferred_locations": ["Remote"],
    }
    score = JobHunterAgent.score_job(job, query="llm engineer", location="US", profile=profile)
    assert score >= 5.0
