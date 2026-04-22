from __future__ import annotations

from PyQt6.QtWidgets import (
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)


class AddPatientDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("환자 추가")
        self.resize(420, 240)

        layout = QVBoxLayout(self)
        title = QLabel("환자 추가")
        title.setStyleSheet("font-size: 18px; font-weight: 700;")
        layout.addWidget(title)

        form = QFormLayout()
        self.patient_id_input = QLineEdit()
        self.patient_id_input.setPlaceholderText("예: patient_003")
        self.patient_id_input.setClearButtonEnabled(True)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("예: 김하늘")
        self.name_input.setClearButtonEnabled(True)
        self.bed_input = QLineEdit()
        self.bed_input.setPlaceholderText("예: A-103")
        self.bed_input.setClearButtonEnabled(True)
        form.addRow("환자 ID", self.patient_id_input)
        form.addRow("이름", self.name_input)
        form.addRow("병상", self.bed_input)
        layout.addLayout(form)

        actions = QHBoxLayout()
        actions.addStretch(1)
        cancel_btn = QPushButton("취소")
        cancel_btn.setObjectName("Ghost")
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("추가")
        save_btn.clicked.connect(self.accept)
        actions.addWidget(cancel_btn)
        actions.addWidget(save_btn)
        layout.addLayout(actions)

    def get_values(self) -> tuple[str, str, str]:
        return (
            self.patient_id_input.text().strip(),
            self.name_input.text().strip(),
            self.bed_input.text().strip(),
        )

    def set_patient_id(self, patient_id: str) -> None:
        self.patient_id_input.setText(patient_id)
