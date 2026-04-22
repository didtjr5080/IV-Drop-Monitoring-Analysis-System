from __future__ import annotations

from PyQt6.QtWidgets import QApplication


def apply_app_theme(app: QApplication, mode: str = "light") -> None:
    app.setStyleSheet(_get_styles(mode))


def _get_styles(mode: str) -> str:
    if mode == "dark":
        return _dark_styles()
    return _light_styles()


def _light_styles() -> str:
    return """
        QWidget {
            font-family: "Noto Sans KR", "Segoe UI", "Malgun Gothic", sans-serif;
            color: #1b1f2a;
        }
        QMainWindow {
            background: #f5f7fb;
        }
        QFrame#HeaderBar {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                      stop:0 #fefefe, stop:1 #eef3ff);
            border-bottom: 1px solid #dce3f1;
        }
        QFrame#Sidebar {
            background: #ffffff;
            border-right: 1px solid #e3e8f4;
        }
        QFrame#RightPanel {
            background: #ffffff;
            border-left: 1px solid #e3e8f4;
        }
        QFrame#Card {
            background: #ffffff;
            border: 1px solid #e1e7f3;
            border-radius: 14px;
        }
        QLabel#SectionTitle {
            font-weight: 600;
            font-size: 15px;
        }
        QLineEdit {
            background: #f2f5fb;
            border: 1px solid #e1e7f3;
            border-radius: 10px;
            padding: 8px 12px;
        }
        QFormLayout QLabel {
            color: #5c677d;
        }
        QComboBox {
            background: #f2f5fb;
            border: 1px solid #e1e7f3;
            border-radius: 10px;
            padding: 6px 10px;
        }
        QPushButton {
            background: #2d6cdf;
            color: #ffffff;
            border: none;
            border-radius: 10px;
            padding: 8px 14px;
            font-weight: 600;
        }
        QPushButton:hover {
            background: #245bc0;
        }
        QPushButton#Ghost {
            background: #f2f5fb;
            color: #2d6cdf;
            border: 1px solid #d6def2;
        }
        QPushButton#Ghost:hover {
            background: #e9f0ff;
            border: 1px solid #b9c9ef;
        }
        QCheckBox {
            spacing: 8px;
        }
        QListWidget {
            background: transparent;
            border: none;
        }
        QListWidget::item {
            padding: 10px 12px;
            border-radius: 10px;
        }
        QListWidget::item:selected {
            background: #e9f0ff;
            color: #1b1f2a;
        }
        QTableWidget {
            border: none;
            background: transparent;
            gridline-color: #e6ecf5;
        }
        QHeaderView::section {
            background: #f2f5fb;
            border: none;
            padding: 6px 8px;
            font-weight: 600;
        }
        QScrollBar:vertical {
            background: transparent;
            width: 8px;
            margin: 2px;
        }
        QScrollBar::handle:vertical {
            background: #c9d5ef;
            border-radius: 4px;
        }
        """


def _dark_styles() -> str:
    return """
        QWidget {
            font-family: "Noto Sans KR", "Segoe UI", "Malgun Gothic", sans-serif;
            color: #e6edf7;
        }
        QMainWindow {
            background: #11141c;
        }
        QFrame#HeaderBar {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                      stop:0 #1a1f2b, stop:1 #161b26);
            border-bottom: 1px solid #293042;
        }
        QFrame#Sidebar {
            background: #151a24;
            border-right: 1px solid #293042;
        }
        QFrame#RightPanel {
            background: #151a24;
            border-left: 1px solid #293042;
        }
        QFrame#Card {
            background: #1b2130;
            border: 1px solid #2b3448;
            border-radius: 14px;
        }
        QLabel#SectionTitle {
            font-weight: 600;
            font-size: 15px;
        }
        QLineEdit {
            background: #1f2635;
            border: 1px solid #2b3448;
            border-radius: 10px;
            padding: 8px 12px;
        }
        QFormLayout QLabel {
            color: #9aa4b2;
        }
        QComboBox {
            background: #1f2635;
            border: 1px solid #2b3448;
            border-radius: 10px;
            padding: 6px 10px;
        }
        QPushButton {
            background: #2d6cdf;
            color: #ffffff;
            border: none;
            border-radius: 10px;
            padding: 8px 14px;
            font-weight: 600;
        }
        QPushButton:hover {
            background: #245bc0;
        }
        QPushButton#Ghost {
            background: #1f2635;
            color: #8fb4ff;
            border: 1px solid #2b3448;
        }
        QPushButton#Ghost:hover {
            background: #273048;
            border: 1px solid #3b4660;
        }
        QCheckBox {
            spacing: 8px;
        }
        QListWidget {
            background: transparent;
            border: none;
        }
        QListWidget::item {
            padding: 10px 12px;
            border-radius: 10px;
        }
        QListWidget::item:selected {
            background: #273048;
            color: #e6edf7;
        }
        QTableWidget {
            border: none;
            background: transparent;
            gridline-color: #2b3448;
        }
        QHeaderView::section {
            background: #1f2635;
            border: none;
            padding: 6px 8px;
            font-weight: 600;
        }
        QScrollBar:vertical {
            background: transparent;
            width: 8px;
            margin: 2px;
        }
        QScrollBar::handle:vertical {
            background: #3b4660;
            border-radius: 4px;
        }
        """
