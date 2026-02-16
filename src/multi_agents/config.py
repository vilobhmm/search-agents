from __future__ import annotations

import json
import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(slots=True)
class Settings:
    telegram_bot_token: str = ""
    telegram_allowed_chat_id: str = ""
    user_profile_json: str = "{}"

    @property
    def user_profile(self) -> dict:
        try:
            data = json.loads(self.user_profile_json or "{}")
            return data if isinstance(data, dict) else {}
        except json.JSONDecodeError:
            return {}


def load_settings() -> Settings:
    load_dotenv()
    return Settings(
        telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
        telegram_allowed_chat_id=os.getenv("TELEGRAM_ALLOWED_CHAT_ID", ""),
        user_profile_json=os.getenv("USER_PROFILE_JSON", "{}"),
    )
