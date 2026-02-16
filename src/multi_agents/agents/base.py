from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(slots=True)
class AgentStatus:
    name: str
    mode: str
    last_heartbeat_utc: str


class BaseAgent:
    name = "base"

    def heartbeat(self, mode: str = "active") -> AgentStatus:
        return AgentStatus(
            name=self.name,
            mode=mode,
            last_heartbeat_utc=datetime.now(timezone.utc).isoformat(),
        )
