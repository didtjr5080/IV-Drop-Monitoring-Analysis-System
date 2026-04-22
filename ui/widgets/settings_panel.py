from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class SettingsPanel(QWidget):
    back_requested = pyqtSignal()
    apply_requested = pyqtSignal(bool, object)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        header = QHBoxLayout()
        title = QLabel("설정")
        title.setStyleSheet("font-size: 18px; font-weight: 700;")
        back_btn = QPushButton("대시보드로")
        back_btn.setObjectName("Ghost")
        back_btn.clicked.connect(self.back_requested.emit)
        header.addWidget(title)
        header.addStretch(1)
        header.addWidget(back_btn)
        layout.addLayout(header)

        appearance_card = self._card("화면 설정")
        appearance_layout = appearance_card.layout()

        self.dark_mode_checkbox = QCheckBox("다크 모드")
        appearance_layout.addWidget(self.dark_mode_checkbox)

        res_row = QHBoxLayout()
        res_label = QLabel("해상도")
        res_label.setStyleSheet("color: #5c677d;")
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItem("1600 x 900 (16:9)", (1600, 900))
        self.resolution_combo.addItem("1920 x 1080 (16:9)", (1920, 1080))
        self.resolution_combo.addItem("1366 x 768 (16:9)", (1366, 768))
        self.resolution_combo.addItem("1440 x 900 (16:10)", (1440, 900))
        self.resolution_combo.addItem("1280 x 800 (16:10)", (1280, 800))
        self.resolution_combo.addItem("1680 x 1050 (16:10)", (1680, 1050))
        self.resolution_combo.addItem("1280 x 720 (16:9)", (1280, 720))
        self.resolution_combo.addItem("1536 x 864 (16:9)", (1536, 864))
        self.resolution_combo.addItem("1280 x 960 (4:3)", (1280, 960))
        self.resolution_combo.addItem("1024 x 768 (4:3)", (1024, 768))
        res_row.addWidget(res_label)
        res_row.addStretch(1)
        res_row.addWidget(self.resolution_combo)
        appearance_layout.addLayout(res_row)

        layout.addWidget(appearance_card)

        actions = QHBoxLayout()
        actions.addStretch(1)
        apply_btn = QPushButton("적용")
        apply_btn.clicked.connect(self._emit_apply)
        actions.addWidget(apply_btn)
        layout.addLayout(actions)

        layout.addStretch(1)

    def _card(self, title: str) -> QFrame:
        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setSpacing(12)
        label = QLabel(title)
        label.setObjectName("SectionTitle")
        card_layout.addWidget(label)
        return card

    def _emit_apply(self) -> None:
        dark_mode = self.dark_mode_checkbox.isChecked()
        resolution = self.resolution_combo.currentData()
        if isinstance(resolution, tuple):
            self.apply_requested.emit(dark_mode, resolution)
