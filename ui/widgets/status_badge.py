from __future__ import annotations

from PyQt6.QtWidgets import QLabel


class StatusBadge(QLabel):
    def __init__(self, text: str, status: str, parent=None) -> None:
        super().__init__(text, parent)
        self.setObjectName("StatusBadge")
        self.set_status(status)

    def set_status(self, status: str) -> None:
        color = {
            "NORMAL": "#2f9e44",
            "WARNING": "#f59f00",
            "ALERT": "#e03131",
        }.get(status, "#2f9e44")
        self.setStyleSheet(
            """
            QLabel {
                background: %s;
                color: #ffffff;
                padding: 2px 8px;
                border-radius: 8px;
                font-weight: 600;
            }
            """
            % color
        )
