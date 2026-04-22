from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Session:
    session_id: str
    start_time: datetime
    end_time: datetime | None
    total_drops: int
    avg_rate: float
    warning_count: int
    alert_count: int
