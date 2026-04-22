from __future__ import annotations

from datetime import datetime


def format_ts(ts: datetime) -> str:
    return ts.strftime("%Y-%m-%d %H:%M:%S")
