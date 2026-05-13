# Search Agents Harness: Job Hunter + CC Multi-Agent Team

Production-style starter for a **specialized, proactive, personalized** multi-agent system:

- **@job_hunter**: tracks AI/tech openings, filters by your profile, and summarizes actions.
- **@cc**: chief coordinator that plans your day, merges agent outputs, and proposes next steps.
- **Telegram control**: run the team from your phone.
- **CLI**: run end-to-end, scrape jobs, execute daily briefing loops.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
```

Edit `.env` and set at least:

- `TELEGRAM_BOT_TOKEN` (for Telegram mode)
- `TELEGRAM_ALLOWED_CHAT_ID` (optional security lock)
- `USER_PROFILE_JSON` (optional, JSON profile for ranking)

## Run end-to-end from CLI

```bash
search-agents e2e --query "remote ai product roles" --location "US"
```

## Start Telegram bot

```bash
search-agents telegram
```

Then from your phone:

- `/brief` => full CC daily briefing
- `/jobs remote llm engineer` => filtered roles from Job Hunter
- `/pulse` => team heartbeat
- `/helpme` => command summary

## Architecture

- `src/multi_agents/agents/job_hunter.py`: source adapters + relevance scoring.
- `src/multi_agents/agents/cc.py`: coordinator and daily briefing composer.
- `src/multi_agents/team.py`: orchestrates agents as a single workflow.
- `src/multi_agents/telegram_bot.py`: Telegram controller.
- `docs/agents/*`: operational markdown (`agents.md`, `soul.md`, `heartbeat.md`, etc.).

## Tests

```bash
pytest
```
