from __future__ import annotations

import sys
from PyQt6.QtWidgets import QApplication

from ui.main_window import MainWindow
from ui.styles.theme import apply_app_theme
from utils.user_settings import load_user_settings


def main() -> None:
    app = QApplication(sys.argv)
    user_settings = load_user_settings()
    apply_app_theme(app, user_settings.theme_mode)

    window = MainWindow(
        initial_theme=user_settings.theme_mode,
        initial_resolution=user_settings.resolution,
    )
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
