from multi_agents.agents.job_hunter import (
    JobHunterAgent,
    extract_companies_from_query,
)


def test_score_job_rewards_query_and_location():
    job = {
        "title": "Senior LLM Engineer",
        "location": "Remote - US",
        "company": "OpenAI",
    }
    profile = {
        "skills": ["python", "llm"],
        "target_roles": ["engineer"],
        "preferred_locations": ["Remote"],
    }
    score = JobHunterAgent.score_job(job, query="llm engineer", location="US", profile=profile)
    assert score >= 5.0


def test_extract_companies_from_query():
    q = "java roles from accenture, cognizant, infosys and google"
    companies = extract_companies_from_query(q)
    assert companies == ["accenture", "cognizant", "infosys", "google"]
