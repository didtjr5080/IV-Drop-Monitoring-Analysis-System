from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QHeaderView, QTableWidget, QTableWidgetItem

from models.session import Session
from utils.datetime_utils import format_ts


class SessionTable(QTableWidget):
    session_selected = pyqtSignal(Session)

    def __init__(self, parent=None) -> None:
        super().__init__(0, 6, parent)
        self.setHorizontalHeaderLabels(
            ["세션", "시작", "종료", "평균 속도", "WARNING", "ALERT"]
        )
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.verticalHeader().setVisible(False)
        self.setSelectionBehavior(self.SelectionBehavior.SelectRows)
        self.setEditTriggers(self.EditTrigger.NoEditTriggers)
        self.cellClicked.connect(self._emit_selected)
        self._sessions: list[Session] = []

    def set_sessions(self, sessions: list[Session]) -> None:
        self._sessions = sessions
        self.setRowCount(len(sessions))
        for row, session in enumerate(sessions):
            self.setItem(row, 0, QTableWidgetItem(session.session_id))
            self.setItem(row, 1, QTableWidgetItem(format_ts(session.start_time)))
            end_text = format_ts(session.end_time) if session.end_time else "-"
            self.setItem(row, 2, QTableWidgetItem(end_text))
            self.setItem(row, 3, QTableWidgetItem(f"{session.avg_rate:.1f}"))
            self.setItem(row, 4, QTableWidgetItem(str(session.warning_count)))
            self.setItem(row, 5, QTableWidgetItem(str(session.alert_count)))

    def _emit_selected(self, row: int, _: int) -> None:
        if 0 <= row < len(self._sessions):
            self.session_selected.emit(self._sessions[row])

    def get_selected_session(self) -> Session | None:
        row = self.currentRow()
        if 0 <= row < len(self._sessions):
            return self._sessions[row]
        return None
