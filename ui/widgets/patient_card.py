from __future__ import annotations

from PyQt6.QtWidgets import QFrame, QGridLayout, QLabel

from models.patient import Patient
from ui.widgets.status_badge import StatusBadge


class PatientCard(QFrame):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("Card")
        layout = QGridLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setHorizontalSpacing(16)
        layout.setVerticalSpacing(6)

        self.name_label = QLabel("환자 선택 필요")
        self.name_label.setStyleSheet("font-size: 18px; font-weight: 700;")
        self.info_label = QLabel("-")
        self.info_label.setStyleSheet("color: #5c677d;")
        self.status_badge = StatusBadge("NORMAL", "NORMAL")

        layout.addWidget(self.name_label, 0, 0)
        layout.addWidget(self.status_badge, 0, 1)
        layout.addWidget(self.info_label, 1, 0, 1, 2)
        layout.setColumnStretch(0, 1)

    def update_patient(self, patient: Patient, status: str) -> None:
        self.name_label.setText(patient.name)
        self.info_label.setText(f"ID: {patient.patient_id}  ·  병상 {patient.bed_number}")
        self.status_badge.setText(status)
        self.status_badge.set_status(status)
