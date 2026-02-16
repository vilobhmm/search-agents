from __future__ import annotations

import json

import typer
from rich.console import Console
from rich.table import Table

from multi_agents.config import load_settings
from multi_agents.team import AgentTeam
from multi_agents.telegram_bot import run_telegram_bot

app = typer.Typer(no_args_is_help=True)
console = Console()


def _parse_companies(companies: str) -> list[str]:
    if not companies.strip():
        return []
    return [x.strip() for x in companies.split(",") if x.strip()]


@app.command()
def e2e(
    query: str = "llm engineer",
    location: str = "",
    companies: str = "",
    limit: int = 10,
) -> None:
    """Run Job Hunter + CC full workflow."""
    settings = load_settings()
    team = AgentTeam()
    parsed_companies = _parse_companies(companies)
    result = team.run(
        query=query,
        location=location,
        profile=settings.user_profile,
        companies=parsed_companies or None,
        limit=limit,
    )

    console.print(f"[bold green]{result.briefing.headline}[/bold green]")
    if result.requested_companies:
        console.print(f"[bold]Requested Companies:[/bold] {', '.join(result.requested_companies)}")

    table = Table(title="Top Opportunities")
    table.add_column("#")
    table.add_column("Company")
    table.add_column("Title")
    table.add_column("Location")
    table.add_column("Score")
    table.add_column("Link")

    for idx, job in enumerate(result.jobs, start=1):
        table.add_row(str(idx), job.company, job.title, job.location, str(job.score), job.absolute_url)

    console.print(table)

    if result.guidance:
        gtable = Table(title="Official Career Site Guidance")
        gtable.add_column("Company")
        gtable.add_column("Official Careers URL")
        gtable.add_column("Note")
        for item in result.guidance:
            gtable.add_row(item.company, item.official_careers_url or "N/A", item.note)
        console.print(gtable)

    console.print("[bold]Priorities[/bold]")
    for p in result.briefing.priorities:
        console.print(f"- {p}")

    console.print("[bold]Next Steps[/bold]")
    for s in result.briefing.next_steps:
        console.print(f"- {s}")

    console.print("[bold]Heartbeat[/bold]")
    console.print(json.dumps(result.heartbeat, indent=2))


@app.command()
def telegram() -> None:
    """Run Telegram bot controller."""
    settings = load_settings()
    if not settings.telegram_bot_token:
        raise typer.BadParameter("Missing TELEGRAM_BOT_TOKEN in environment.")

    run_telegram_bot(token=settings.telegram_bot_token, allowed_chat_id=settings.telegram_allowed_chat_id)


if __name__ == "__main__":
    app()
