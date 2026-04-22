from __future__ import annotations

from dataclasses import dataclass
from statistics import mean

from models.log import Log


@dataclass(frozen=True)
class AnalysisResult:
    avg_rate: float
    max_rate: float
    min_rate: float
    warning_count: int
    alert_count: int
    stability_score: int
    trend: str


def _safe_mean(values: list[float]) -> float:
    return mean(values) if values else 0.0


def analyze_logs(logs: list[Log]) -> AnalysisResult:
    rates = [log.rate_per_min for log in logs]
    avg_rate = _safe_mean(rates)
    max_rate = max(rates) if rates else 0.0
    min_rate = min(rates) if rates else 0.0
    warning_count = sum(1 for log in logs if log.status == "WARNING")
    alert_count = sum(1 for log in logs if log.status == "ALERT")

    if rates:
        mad = _safe_mean([abs(r - avg_rate) for r in rates])
        if avg_rate > 0:
            score = max(0.0, 100.0 - (mad / avg_rate) * 100.0)
        else:
            score = 0.0
    else:
        score = 0.0

    stability_score = int(round(score))

    if len(rates) >= 4:
        half = len(rates) // 2
        first_avg = _safe_mean(rates[:half])
        second_avg = _safe_mean(rates[half:])
        delta = second_avg - first_avg
        threshold = max(1.0, first_avg * 0.1)
        if delta > threshold:
            trend = "증가"
        elif delta < -threshold:
            trend = "감소"
        else:
            trend = "안정"
    else:
        trend = "안정"

    return AnalysisResult(
        avg_rate=avg_rate,
        max_rate=max_rate,
        min_rate=min_rate,
        warning_count=warning_count,
        alert_count=alert_count,
        stability_score=stability_score,
        trend=trend,
    )
