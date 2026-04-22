from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

from models.patient import Patient
from utils.resource_utils import resolve_asset


class Sidebar(QFrame):
    patient_selected = pyqtSignal(Patient)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self._patients: list[Patient] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(16)

        header = QHBoxLayout()
        logo = QLabel()
        logo.setPixmap(QIcon(resolve_asset("assets/icons/app_logo.svg")).pixmap(32, 32))
        title = QLabel("IV Drop Monitor")
        title.setStyleSheet("font-size: 18px; font-weight: 700;")
        header.addWidget(logo)
        header.addWidget(title)
        header.addStretch(1)
        layout.addLayout(header)

        search_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("환자 검색 (이름/ID)")
        search_icon = QIcon(resolve_asset("assets/icons/search.svg"))
        self.search_input.addAction(search_icon, QLineEdit.ActionPosition.LeadingPosition)
        self.search_input.textChanged.connect(self._apply_filter)
        search_row.addWidget(self.search_input)
        layout.addLayout(search_row)

        self.patient_list = QListWidget()
        self.patient_list.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self.patient_list, 1)

    def set_patients(self, patients: list[Patient]) -> None:
        self._patients = patients
        self._render_list(patients)

    def _render_list(self, patients: list[Patient]) -> None:
        self.patient_list.clear()
        patient_icon = QIcon(resolve_asset("assets/icons/patient.svg"))
        for patient in patients:
            item = QListWidgetItem(
                patient_icon, f"{patient.name}  ·  {patient.patient_id}"
            )
            item.setData(Qt.ItemDataRole.UserRole, patient)
            self.patient_list.addItem(item)

    def _apply_filter(self, text: str) -> None:
        query = text.strip().lower()
        if not query:
            self._render_list(self._patients)
            return
        filtered = [
            p
            for p in self._patients
            if query in p.name.lower() or query in p.patient_id.lower()
        ]
        self._render_list(filtered)

    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        patient = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(patient, Patient):
            self.patient_selected.emit(patient)
