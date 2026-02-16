from __future__ import annotations

import asyncio

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from multi_agents.config import load_settings
from multi_agents.team import AgentTeam


def _allowed(update: Update, allowed_chat_id: str) -> bool:
    if not allowed_chat_id:
        return True
    chat = update.effective_chat
    return bool(chat and str(chat.id) == str(allowed_chat_id))


async def _helpme(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Commands:\n"
        "/brief - Full daily briefing\n"
        "/jobs <query words> - Search jobs\n"
        "/pulse - Agent heartbeat"
    )


async def _brief(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings = load_settings()
    if not _allowed(update, settings.telegram_allowed_chat_id):
        return

    team = AgentTeam()
    result = team.run(query="llm engineer", location="", profile=settings.user_profile, limit=5)
    lines = [result.briefing.headline, "", "Top opportunities:"]
    lines.extend(result.briefing.opportunities)
    lines.append("")
    lines.append("Next steps:")
    lines.extend(f"- {x}" for x in result.briefing.next_steps)
    await update.message.reply_text("\n".join(lines))


async def _jobs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings = load_settings()
    if not _allowed(update, settings.telegram_allowed_chat_id):
        return

    query = " ".join(context.args).strip() or "llm engineer"
    team = AgentTeam()
    result = team.run(query=query, location="", profile=settings.user_profile, limit=5)
    lines = [f"Results for: {query}"]
    for j in result.jobs:
        lines.append(f"- {j.title} @ {j.company} ({j.location})\n  {j.absolute_url}")
    await update.message.reply_text("\n".join(lines))


async def _pulse(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings = load_settings()
    if not _allowed(update, settings.telegram_allowed_chat_id):
        return

    team = AgentTeam()
    result = team.run(query="llm engineer", location="", profile=settings.user_profile, limit=1)
    pulse = result.heartbeat
    await update.message.reply_text(
        f"job_hunter={pulse['job_hunter']['mode']}\ncc={pulse['cc']['mode']}\n"
        f"ts={pulse['cc']['last_heartbeat_utc']}"
    )


def run_telegram_bot(token: str, allowed_chat_id: str = "") -> None:
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("help", _helpme))
    application.add_handler(CommandHandler("helpme", _helpme))
    application.add_handler(CommandHandler("brief", _brief))
    application.add_handler(CommandHandler("jobs", _jobs))
    application.add_handler(CommandHandler("pulse", _pulse))

    # keep explicit loop handling to work from CLI entrypoints and scripts
    asyncio.run(application.run_polling(close_loop=False, allowed_updates=Update.ALL_TYPES))
