from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Skill:
    name: str
    description: str


JOB_HUNTER_SKILLS = [
    Skill("career-page-scraping", "Fetches and normalizes jobs from greenhouse-style APIs."),
    Skill("fit-scoring", "Ranks jobs against user skills, location, and role preferences."),
    Skill("change-monitoring", "Enables repeated runs for new posting detection."),
]

CC_SKILLS = [
    Skill("daily-briefing", "Builds concise plans from current job pipeline and priorities."),
    Skill("coordination", "Delegates to Job Hunter and merges outputs into action plans."),
    Skill("follow-up-suggestions", "Provides proactive next actions for applications."),
]
