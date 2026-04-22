from __future__ import annotations

from PyQt6.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout, QWidget

from services.analysis_service import AnalysisResult


class SummaryCards(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setHorizontalSpacing(12)
        layout.setVerticalSpacing(12)
        self._cards: dict[str, QLabel] = {}

        fields = [
            ("평균 속도", "avg_rate"),
            ("최대 속도", "max_rate"),
            ("최소 속도", "min_rate"),
            ("WARNING", "warning_count"),
            ("ALERT", "alert_count"),
            ("안정성 점수", "stability_score"),
            ("추세", "trend"),
        ]

        for idx, (title, key) in enumerate(fields):
            card = self._create_card(title)
            row, col = divmod(idx, 4)
            layout.addWidget(card, row, col)
            self._cards[key] = card.findChild(QLabel, "ValueLabel")

    def update_metrics(self, result: AnalysisResult | None) -> None:
        if result is None:
            for label in self._cards.values():
                label.setText("-")
            return

        self._cards["avg_rate"].setText(f"{result.avg_rate:.1f}")
        self._cards["max_rate"].setText(f"{result.max_rate:.1f}")
        self._cards["min_rate"].setText(f"{result.min_rate:.1f}")
        self._cards["warning_count"].setText(str(result.warning_count))
        self._cards["alert_count"].setText(str(result.alert_count))
        self._cards["stability_score"].setText(f"{result.stability_score}")
        self._cards["trend"].setText(result.trend)

    def _create_card(self, title: str) -> QFrame:
        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(14, 14, 14, 14)
        card_layout.setSpacing(6)
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #5c677d; font-weight: 600;")
        value_label = QLabel("-")
        value_label.setObjectName("ValueLabel")
        value_label.setStyleSheet("font-size: 18px; font-weight: 700;")
        card_layout.addWidget(title_label)
        card_layout.addWidget(value_label)
        return card
