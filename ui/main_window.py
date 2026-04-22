from __future__ import annotations

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QFileDialog,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
    QMainWindow,
)

from config.settings import SETTINGS
from models.patient import Patient
from models.session import Session
from services.analysis_service import AnalysisResult, analyze_logs
from services.report_service import SessionReport, export_patient_report
from services.firebase_service import FirestoreService
from services.mock_data_service import MockDataService
from ui.widgets.charts_panel import ChartsPanel
from ui.widgets.logs_panel import LogsPanel
from ui.widgets.log_detail_dialog import LogDetailDialog
from ui.widgets.patient_card import PatientCard
from ui.widgets.session_table import SessionTable
from ui.widgets.sidebar import Sidebar
from ui.widgets.summary_cards import SummaryCards
from ui.widgets.settings_panel import SettingsPanel
from ui.styles.theme import apply_app_theme
from utils.resource_utils import resolve_asset
from utils.user_settings import UserSettings, load_user_settings, save_user_settings


class MainWindow(QMainWindow):
    def __init__(
        self,
        initial_theme: str | None = None,
        initial_resolution: tuple[int, int] | None = None,
    ) -> None:
        super().__init__()
        user_settings = load_user_settings()
        theme = initial_theme or user_settings.theme_mode
        resolution = initial_resolution or user_settings.resolution
        self.setWindowTitle("IV Drop Monitoring")
        self.resize(resolution[0], resolution[1])

        root = QWidget()
        self.setCentralWidget(root)
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self.header = self._build_header()
        root_layout.addWidget(self.header)

        content = QHBoxLayout()
        content.setContentsMargins(0, 0, 0, 0)
        content.setSpacing(0)

        self.sidebar = Sidebar()
        self.sidebar.setFixedWidth(280)
        self.sidebar.patient_selected.connect(self._on_patient_selected)
        content.addWidget(self.sidebar)

        self.center_panel = self._build_center_panel()
        self.settings_panel = SettingsPanel()
        self.settings_panel.back_requested.connect(self._show_dashboard)
        self.settings_panel.apply_requested.connect(self._apply_settings)

        self.center_stack = QStackedWidget()
        self.center_stack.addWidget(self.center_panel)
        self.center_stack.addWidget(self.settings_panel)
        content.addWidget(self.center_stack, 1)

        self.logs_panel = LogsPanel()
        self.logs_panel.setFixedWidth(360)
        self.logs_panel.timeline_double_clicked.connect(self._show_log_details)
        content.addWidget(self.logs_panel)

        root_layout.addLayout(content, 1)

        self.current_patient: Patient | None = None
        self.current_session: Session | None = None
        self.theme_mode = theme
        self.data_service = self._init_service()

        self.refresh_timer = QTimer(self)
        self.refresh_timer.setInterval(500)
        self.refresh_timer.timeout.connect(self._reload_current)
        self.refresh_timer.start()

        self._load_patients()

    def _build_header(self) -> QFrame:
        header = QFrame()
        header.setObjectName("HeaderBar")
        layout = QHBoxLayout(header)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(12)

        icon = QLabel()
        icon.setPixmap(QIcon(resolve_asset("assets/icons/app_logo.svg")).pixmap(28, 28))
        title = QLabel("수액 점적 모니터링 및 분석")
        title.setStyleSheet("font-size: 18px; font-weight: 700;")
        subtitle = QLabel("실시간 관제 대시보드")
        subtitle.setStyleSheet("color: #5c677d;")

        self.status_label = QLabel("● 연결됨")
        self.status_label.setStyleSheet("color: #2f9e44; font-weight: 600;")

        refresh_btn = QPushButton("새로고침")
        refresh_btn.setObjectName("Ghost")
        refresh_btn.setIcon(QIcon(resolve_asset("assets/icons/refresh.svg")))
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.clicked.connect(self._reload_current)

        export_btn = QPushButton("레포트")
        export_btn.setObjectName("Ghost")
        export_btn.setIcon(QIcon(resolve_asset("assets/icons/chart.svg")))
        export_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        export_btn.clicked.connect(self._export_report)

        self.settings_btn = QPushButton("설정")
        self.settings_btn.setObjectName("Ghost")
        self.settings_btn.setIcon(QIcon(resolve_asset("assets/icons/settings.svg")))
        self.settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.settings_btn.clicked.connect(self._show_settings)

        layout.addWidget(icon)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addStretch(1)
        layout.addWidget(self.status_label)
        layout.addWidget(refresh_btn)
        layout.addWidget(export_btn)
        layout.addWidget(self.settings_btn)
        return header

    def _build_center_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self.patient_card = PatientCard()
        layout.addWidget(self.patient_card)

        sessions_header = QHBoxLayout()
        sessions_title = QLabel("세션 목록")
        sessions_title.setObjectName("SectionTitle")
        sessions_header.addWidget(sessions_title)
        sessions_header.addStretch(1)
        delete_btn = QPushButton("세션 삭제")
        delete_btn.setObjectName("Ghost")
        delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        delete_btn.clicked.connect(self._delete_selected_session)
        sessions_header.addWidget(delete_btn)
        layout.addLayout(sessions_header)

        self.session_table = SessionTable()
        self.session_table.session_selected.connect(self._on_session_selected)
        layout.addWidget(self.session_table, 1)

        summary_title = QLabel("분석 요약")
        summary_title.setObjectName("SectionTitle")
        layout.addWidget(summary_title)

        self.summary_cards = SummaryCards()
        layout.addWidget(self.summary_cards)

        charts_title = QLabel("그래프")
        charts_title.setObjectName("SectionTitle")
        layout.addWidget(charts_title)

        self.charts_panel = ChartsPanel()
        layout.addWidget(self.charts_panel, 2)

        return panel

    def _init_service(self):
        if SETTINGS.use_mock_data:
            self._set_connection_status("MOCK", "#5c677d")
            return MockDataService()

        try:
            service = FirestoreService(str(SETTINGS.firestore_service_account))
            service.connect()
            self._set_connection_status("연결됨", "#2f9e44")
            return service
        except Exception as exc:
            self._show_error(
                "Firestore 연결 실패",
                f"Firestore 연결에 실패했습니다.\n{exc}",
            )
            self._set_connection_status("오프라인", "#e03131")
            return MockDataService()

    def _show_error(self, title: str, message: str) -> None:
        dialog = QMessageBox(self)
        dialog.setIcon(QMessageBox.Icon.Critical)
        dialog.setWindowTitle(title)
        dialog.setText(message)
        dialog.exec()

    def _set_connection_status(self, text: str, color: str) -> None:
        self.status_label.setText(f"● {text}")
        self.status_label.setStyleSheet(f"color: {color}; font-weight: 600;")

    def _show_settings(self) -> None:
        self.settings_panel.dark_mode_checkbox.setChecked(self.theme_mode == "dark")
        current_size = (self.width(), self.height())
        index = self.settings_panel.resolution_combo.findData(current_size)
        if index >= 0:
            self.settings_panel.resolution_combo.setCurrentIndex(index)
        self.center_stack.setCurrentWidget(self.settings_panel)
        self.settings_btn.setText("대시보드")

    def _show_dashboard(self) -> None:
        self.center_stack.setCurrentWidget(self.center_panel)
        self.settings_btn.setText("설정")

    def _apply_settings(self, dark_mode: bool, resolution: tuple[int, int]) -> None:
        mode = "dark" if dark_mode else "light"
        self.theme_mode = mode
        app = QApplication.instance()
        if app is not None:
            apply_app_theme(app, mode)
        width, height = resolution
        self.resize(width, height)
        save_user_settings(UserSettings(theme_mode=mode, resolution=resolution))

    def closeEvent(self, event) -> None:
        if self.refresh_timer.isActive():
            self.refresh_timer.stop()
        size = (self.width(), self.height())
        save_user_settings(UserSettings(theme_mode=self.theme_mode, resolution=size))
        super().closeEvent(event)

    def _load_patients(self) -> None:
        patients = self.data_service.get_patients()
        self.sidebar.set_patients(patients)

    def _on_patient_selected(self, patient: Patient) -> None:
        self.current_patient = patient
        sessions = self.data_service.get_sessions(patient.patient_id)
        self.session_table.set_sessions(sessions)
        status = "NORMAL"
        if sessions:
            if sessions[0].alert_count > 0:
                status = "ALERT"
            elif sessions[0].warning_count > 0:
                status = "WARNING"
        self.patient_card.update_patient(patient, status)
        self.summary_cards.update_metrics(None)
        self.charts_panel.update_charts([])
        self.logs_panel.update_logs([])

    def _on_session_selected(self, session: Session) -> None:
        if not self.current_patient:
            return
        self.current_session = session
        logs = self.data_service.get_logs(
            self.current_patient.patient_id, session.session_id
        )
        analysis = analyze_logs(logs)
        self.summary_cards.update_metrics(analysis)
        self.charts_panel.update_charts(logs)
        self.logs_panel.update_logs(logs)

    def _reload_current(self) -> None:
        self._load_patients()
        if self.current_patient:
            self._on_patient_selected(self.current_patient)
            if self.current_session:
                self._on_session_selected(self.current_session)

    def _export_report(self) -> None:
        if not self.current_patient:
            self._show_error("레포트", "먼저 환자를 선택하세요.")
            return
        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "레포트 저장",
            f"{self.current_patient.patient_id}_report.pdf",
            "PDF Files (*.pdf)",
        )
        if not output_path:
            return

        try:
            sessions = self.data_service.get_sessions(self.current_patient.patient_id)
            session_reports: list[SessionReport] = []
            for session in sessions:
                logs = self.data_service.get_logs(
                    self.current_patient.patient_id, session.session_id
                )
                analysis = analyze_logs(logs)
                session_reports.append(
                    SessionReport(session=session, analysis=analysis, logs=logs)
                )

            export_patient_report(self.current_patient, session_reports, output_path)
        except Exception as exc:
            self._show_error("레포트 저장 실패", f"저장 중 오류가 발생했습니다.\n{exc}")
            return

        dialog = QMessageBox(self)
        dialog.setIcon(QMessageBox.Icon.Information)
        dialog.setWindowTitle("레포트")
        dialog.setText("PDF 리포트가 저장되었습니다.")
        dialog.exec()

    def _show_log_details(self, log) -> None:
        patient_text = (
            f"{self.current_patient.name} ({self.current_patient.patient_id})"
            if self.current_patient
            else "-"
        )
        session_text = self.current_session.session_id if self.current_session else "-"
        dialog = LogDetailDialog(log, patient_text, session_text, self)
        dialog.exec()

    def _delete_selected_session(self) -> None:
        if not self.current_patient:
            self._show_error("세션 삭제", "먼저 환자를 선택하세요.")
            return
        session = self.session_table.get_selected_session()
        if session is None:
            self._show_error("세션 삭제", "삭제할 세션을 선택하세요.")
            return
        confirm = QMessageBox.question(
            self,
            "세션 삭제",
            f"세션 {session.session_id} 을(를) 삭제할까요?\n하위 로그도 함께 삭제됩니다.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return
        try:
            self.data_service.delete_session(
                self.current_patient.patient_id, session.session_id
            )
        except Exception as exc:
            self._show_error("세션 삭제 실패", f"삭제 중 오류가 발생했습니다.\n{exc}")
            return

        self.current_session = None
        self._on_patient_selected(self.current_patient)
