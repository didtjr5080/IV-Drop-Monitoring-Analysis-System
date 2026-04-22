from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from models.log import Log
from models.patient import Patient
from models.session import Session


@dataclass(frozen=True)
class MockDataService:
    seed: int = 42

    def __post_init__(self) -> None:
        random.seed(self.seed)

    def get_patients(self) -> list[Patient]:
        now = datetime.now(timezone.utc)
        return [
            Patient("P-1001", "김하늘", "A-01", now - timedelta(days=12)),
            Patient("P-1002", "이준호", "A-02", now - timedelta(days=8)),
            Patient("P-1003", "박서연", "B-03", now - timedelta(days=4)),
            Patient("P-1004", "최민수", "C-01", now - timedelta(days=1)),
        ]

    def get_sessions(self, patient_id: str) -> list[Session]:
        base = datetime.now(timezone.utc) - timedelta(hours=12)
        sessions = []
        for idx in range(3):
            start = base - timedelta(hours=idx * 6)
            end = start + timedelta(hours=2 + idx)
            avg_rate = random.uniform(18, 36)
            sessions.append(
                Session(
                    session_id=f"S-{patient_id}-{idx + 1}",
                    start_time=start,
                    end_time=end,
                    total_drops=int(avg_rate * 60),
                    avg_rate=avg_rate,
                    warning_count=random.randint(0, 3),
                    alert_count=random.randint(0, 1),
                )
            )
        return sorted(sessions, key=lambda s: s.start_time, reverse=True)

    def get_logs(self, patient_id: str, session_id: str) -> list[Log]:
        now = datetime.now(timezone.utc) - timedelta(hours=1)
        logs: list[Log] = []
        drop_total = 0
        for i in range(60):
            ts = now + timedelta(minutes=i)
            rate = max(5.0, random.gauss(25.0, 5.0))
            drop_total += int(rate)
            status = "NORMAL"
            if rate > 35:
                status = "WARNING"
            if rate > 42:
                status = "ALERT"
            logs.append(
                Log(
                    timestamp=ts,
                    drop_count=drop_total,
                    rate_per_min=rate,
                    status=status,
                    last_drop_sec=max(1.5, 60.0 / rate),
                )
            )
        return logs

    def delete_session(self, patient_id: str, session_id: str) -> None:
        return
