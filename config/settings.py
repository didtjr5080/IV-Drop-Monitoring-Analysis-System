from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppSettings:
    use_mock_data: bool = False
    firestore_service_account: Path = Path("serviceAccountKey.json")
    window_width: int = 1600
    window_height: int = 900


SETTINGS = AppSettings()
