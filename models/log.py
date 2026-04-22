from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Log:
    timestamp: datetime
    drop_count: int
    rate_per_min: float
    status: str
    last_drop_sec: float
