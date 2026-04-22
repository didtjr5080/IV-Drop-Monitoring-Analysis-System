from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Patient:
    patient_id: str
    name: str
    bed_number: str
    created_at: datetime
