from __future__ import annotations

from PyQt6.QtWidgets import QDialog, QFrame, QGridLayout, QHBoxLayout, QLabel, QVBoxLayout

from models.log import Log
from ui.widgets.status_badge import StatusBadge


class LogDetailDialog(QDialog):
    def __init__(
        self,
        log: Log,
        patient_text: str,
        session_text: str,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("상태 이벤트 상세")
        self.resize(520, 360)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        header = QHBoxLayout()
        title = QLabel("상태 이벤트 상세")
        title.setStyleSheet("font-size: 18px; font-weight: 700;")
        badge = StatusBadge(log.status, log.status)
        header.addWidget(title)
        header.addStretch(1)
        header.addWidget(badge)
        layout.addLayout(header)

        card = QFrame()
        card.setObjectName("Card")
        grid = QGridLayout(card)
        grid.setContentsMargins(16, 16, 16, 16)
        grid.setHorizontalSpacing(24)
        grid.setVerticalSpacing(10)

        self._add_row(grid, 0, "환자", patient_text)
        self._add_row(grid, 1, "세션", session_text)
        self._add_row(grid, 2, "시간", log.timestamp.strftime("%Y-%m-%d %H:%M:%S"))
        self._add_row(grid, 3, "상태", log.status)
        self._add_row(grid, 4, "속도", f"{log.rate_per_min:.2f} drops/min")
        self._add_row(grid, 5, "누적", f"{log.drop_count}")
        self._add_row(grid, 6, "마지막 간격", f"{log.last_drop_sec:.2f} sec")

        layout.addWidget(card)
        layout.addStretch(1)

    def _add_row(self, grid: QGridLayout, row: int, label: str, value: str) -> None:
        key = QLabel(label)
        key.setStyleSheet("color: #5c677d; font-weight: 600;")
        val = QLabel(value)
        val.setStyleSheet("font-weight: 600;")
        grid.addWidget(key, row, 0)
        grid.addWidget(val, row, 1)
