from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QHeaderView,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from models.log import Log
from utils.datetime_utils import format_ts


class LogsPanel(QFrame):
    timeline_double_clicked = pyqtSignal(object)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("RightPanel")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title = QLabel("최근 로그")
        title.setObjectName("SectionTitle")
        layout.addWidget(title)

        self.logs_table = QTableWidget(0, 4)
        self.logs_table.setHorizontalHeaderLabels(
            ["시간", "속도", "누적", "상태"]
        )
        self.logs_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.logs_table.verticalHeader().setVisible(False)
        self.logs_table.setEditTriggers(self.logs_table.EditTrigger.NoEditTriggers)
        layout.addWidget(self.logs_table, 1)

        timeline_title = QLabel("상태 이벤트 타임라인")
        timeline_title.setObjectName("SectionTitle")
        layout.addWidget(timeline_title)

        self.timeline_list = QListWidget()
        self.timeline_list.itemDoubleClicked.connect(self._on_timeline_double_clicked)
        layout.addWidget(self.timeline_list, 1)

    def update_logs(self, logs: list[Log]) -> None:
        self.logs_table.setRowCount(0)
        for log in logs[-20:][::-1]:
            row = self.logs_table.rowCount()
            self.logs_table.insertRow(row)
            self.logs_table.setItem(row, 0, QTableWidgetItem(format_ts(log.timestamp)))
            self.logs_table.setItem(row, 1, QTableWidgetItem(f"{log.rate_per_min:.1f}"))
            self.logs_table.setItem(row, 2, QTableWidgetItem(str(log.drop_count)))
            self.logs_table.setItem(row, 3, QTableWidgetItem(log.status))

        self.timeline_list.clear()
        for log in logs:
            if log.status in {"WARNING", "ALERT"}:
                item = QListWidgetItem(f"{format_ts(log.timestamp)}  ·  {log.status}")
                item.setData(Qt.ItemDataRole.UserRole, log)
                self.timeline_list.addItem(item)

    def _on_timeline_double_clicked(self, item: QListWidgetItem) -> None:
        log = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(log, Log):
            self.timeline_double_clicked.emit(log)
