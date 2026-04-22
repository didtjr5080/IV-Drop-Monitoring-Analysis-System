from __future__ import annotations

from datetime import datetime

from matplotlib import rcParams
from matplotlib import dates as mdates
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from models.log import Log


class ChartWidget(QFrame):
    def __init__(self, title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("Card")
        self._title = title
        self._logs: list[Log] = []
        self._dialog: ChartDialog | None = None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        label = QLabel(title)
        label.setObjectName("SectionTitle")
        layout.addWidget(label)

        self._apply_matplotlib_fonts()
        self.figure = Figure(figsize=(5, 3), tight_layout=True)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.canvas.setCursor(Qt.CursorShape.PointingHandCursor)
        self.canvas.mpl_connect("button_press_event", self._on_click)
        layout.addWidget(self.canvas, 1)

    def plot_rate(self, logs: list[Log]) -> None:
        self._logs = logs
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        if not logs:
            ax.text(0.5, 0.5, "데이터 없음", ha="center", va="center")
            ax.set_axis_off()
        else:
            times = [log.timestamp for log in logs]
            rates = [log.rate_per_min for log in logs]
            ax.plot(times, rates, color="#2d6cdf", linewidth=2, label="Rate/min")
            self._add_markers(ax, logs, lambda log: log.rate_per_min)
            ax.set_ylabel("drops/min")
            ax.set_title("시간 대비 점적 속도")
            ax.grid(True, alpha=0.3)
            ax.legend(loc="upper right")
        self.canvas.draw()
        self._refresh_dialog()

    def plot_cumulative(self, logs: list[Log]) -> None:
        self._logs = logs
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        if not logs:
            ax.text(0.5, 0.5, "데이터 없음", ha="center", va="center")
            ax.set_axis_off()
        else:
            times = [log.timestamp for log in logs]
            drops = [log.drop_count for log in logs]
            ax.plot(times, drops, color="#13a388", linewidth=2, label="Cumulative")
            self._add_markers(ax, logs, lambda log: log.drop_count)
            ax.set_ylabel("drops")
            ax.set_title("시간 대비 누적 점적 수")
            ax.grid(True, alpha=0.3)
            ax.legend(loc="upper left")
        self.canvas.draw()
        self._refresh_dialog()

    def _add_markers(self, ax, logs: list[Log], value_fn) -> None:
        warning_x: list[datetime] = []
        warning_y: list[float] = []
        alert_x: list[datetime] = []
        alert_y: list[float] = []
        for log in logs:
            if log.status == "WARNING":
                warning_x.append(log.timestamp)
                warning_y.append(float(value_fn(log)))
            if log.status == "ALERT":
                alert_x.append(log.timestamp)
                alert_y.append(float(value_fn(log)))
        if warning_x:
            ax.scatter(warning_x, warning_y, color="#f59f00", label="WARNING", s=30)
        if alert_x:
            ax.scatter(alert_x, alert_y, color="#e03131", label="ALERT", s=30)

    def _apply_matplotlib_fonts(self) -> None:
        rcParams["font.family"] = ["Malgun Gothic", "Noto Sans KR", "Segoe UI"]
        rcParams["axes.unicode_minus"] = False

    def _on_click(self, _event) -> None:
        if self._dialog is None:
            self._dialog = ChartDialog(self._title, self._logs, self)
        else:
            self._dialog.update_logs(self._logs)
        self._dialog.exec()

    def _refresh_dialog(self) -> None:
        if self._dialog is not None and self._dialog.isVisible():
            self._dialog.update_logs(self._logs)


class ChartDialog(QDialog):
    def __init__(self, title: str, logs: list[Log], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"확대 보기 - {title}")
        self.resize(1100, 720)
        self._title = title
        self._logs = logs
        self._annotation = None
        self._ax = None
        self._times_num: list[float] = []
        self._values: list[float] = []
        self._base_xlim: tuple[float, float] | None = None
        self._base_ylim: tuple[float, float] | None = None
        self._dragging = False
        self._tracking = False
        self._press_x = 0.0
        self._press_y = 0.0
        self._press_xlim: tuple[float, float] | None = None
        self._press_ylim: tuple[float, float] | None = None
        self._vline = None
        self._hline = None
        self._point = None

        layout = QVBoxLayout(self)
        header = QLabel(title)
        header.setStyleSheet("font-size: 16px; font-weight: 700;")
        layout.addWidget(header)

        self.figure = Figure(figsize=(8, 5), tight_layout=True)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.canvas.setCursor(Qt.CursorShape.CrossCursor)
        self.canvas.mpl_connect("button_press_event", self._on_click)
        self.canvas.mpl_connect("button_press_event", self._on_pan_start)
        self.canvas.mpl_connect("button_release_event", self._on_pan_end)
        self.canvas.mpl_connect("button_release_event", self._on_track_end)
        self.canvas.mpl_connect("scroll_event", self._on_scroll)
        self.canvas.mpl_connect("motion_notify_event", self._on_hover)
        layout.addWidget(self.canvas, 1)

        self._plot(title, logs)

    def _plot(self, title: str, logs: list[Log]) -> None:
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        self._ax = ax
        if not logs:
            ax.text(0.5, 0.5, "데이터 없음", ha="center", va="center")
            ax.set_axis_off()
            self.canvas.draw()
            return

        times = [log.timestamp for log in logs]
        self._times_num = mdates.date2num(times).tolist()
        if "누적" in title:
            values = [float(log.drop_count) for log in logs]
            self._values = values
            ax.plot(times, values, color="#13a388", linewidth=2, label="Cumulative")
            ax.set_ylabel("drops")
            ax.set_title("시간 대비 누적 점적 수")
            warning_y = [log.drop_count for log in logs if log.status == "WARNING"]
            alert_y = [log.drop_count for log in logs if log.status == "ALERT"]
        else:
            values = [float(log.rate_per_min) for log in logs]
            self._values = values
            ax.plot(times, values, color="#2d6cdf", linewidth=2, label="Rate/min")
            ax.set_ylabel("drops/min")
            ax.set_title("시간 대비 점적 속도")
            warning_y = [log.rate_per_min for log in logs if log.status == "WARNING"]
            alert_y = [log.rate_per_min for log in logs if log.status == "ALERT"]

        warning_x = [log.timestamp for log in logs if log.status == "WARNING"]
        alert_x = [log.timestamp for log in logs if log.status == "ALERT"]
        if warning_x:
            ax.scatter(warning_x, warning_y, color="#f59f00", label="WARNING", s=40)
        if alert_x:
            ax.scatter(alert_x, alert_y, color="#e03131", label="ALERT", s=40)
        ax.grid(True, alpha=0.3)
        ax.legend(loc="upper right")
        self._base_xlim = ax.get_xlim()
        self._base_ylim = ax.get_ylim()
        self._annotation = ax.annotate(
            "",
            xy=(0, 0),
            xytext=(10, 10),
            textcoords="offset points",
            bbox=dict(boxstyle="round", fc="#0f172a", ec="none", alpha=0.85),
            color="#ffffff",
        )
        self._annotation.set_visible(False)
        self._vline = ax.axvline(self._times_num[0], color="#94a3b8", linewidth=1, alpha=0.6)
        self._hline = ax.axhline(self._values[0], color="#94a3b8", linewidth=1, alpha=0.6)
        self._point = ax.scatter([self._times_num[0]], [self._values[0]], color="#38bdf8", s=50, zorder=5)
        self._vline.set_visible(False)
        self._hline.set_visible(False)
        self.canvas.draw()

    def update_logs(self, logs: list[Log]) -> None:
        if not logs and self._logs:
            return
        if self._ax is None:
            self._logs = logs
            self._plot(self._title, logs)
            return
        current_xlim = self._ax.get_xlim()
        current_ylim = self._ax.get_ylim()
        self._logs = logs
        self._plot(self._title, logs)
        if self._base_xlim and self._base_ylim:
            x_min = max(self._base_xlim[0], current_xlim[0])
            x_max = min(self._base_xlim[1], current_xlim[1])
            y_min = max(self._base_ylim[0], current_ylim[0])
            y_max = min(self._base_ylim[1], current_ylim[1])
            if x_min < x_max and y_min < y_max:
                self._ax.set_xlim(x_min, x_max)
                self._ax.set_ylim(y_min, y_max)
        self.canvas.draw_idle()

    def _on_click(self, event) -> None:
        if self._ax is None or event.inaxes != self._ax:
            return
        if getattr(event, "dblclick", False):
            self._reset_view()
            return
        if event.button != 1:
            return
        if event.xdata is None or event.ydata is None:
            return
        self._tracking = True
        self._update_annotation(event.xdata, force_draw=True)

    def _on_scroll(self, event) -> None:
        if self._ax is None or event.inaxes != self._ax:
            return
        if not self._is_ctrl_pressed(event):
            return
        if event.xdata is None or event.ydata is None:
            return
        base_scale = self._get_zoom_scale(event)

        x_min, x_max = self._ax.get_xlim()
        y_min, y_max = self._ax.get_ylim()

        x_range = (x_max - x_min) * base_scale
        y_range = (y_max - y_min) * base_scale

        x_center = event.xdata
        y_center = event.ydata

        new_xlim = (x_center - x_range / 2, x_center + x_range / 2)
        new_ylim = (y_center - y_range / 2, y_center + y_range / 2)

        if self._base_xlim and self._base_ylim:
            base_xmin, base_xmax = self._base_xlim
            base_ymin, base_ymax = self._base_ylim
            new_xlim = (
                max(base_xmin, new_xlim[0]),
                min(base_xmax, new_xlim[1]),
            )
            new_ylim = (
                max(base_ymin, new_ylim[0]),
                min(base_ymax, new_ylim[1]),
            )

        self._ax.set_xlim(*new_xlim)
        self._ax.set_ylim(*new_ylim)
        self.canvas.draw_idle()

    def _on_hover(self, event) -> None:
        if self._ax is None or event.inaxes != self._ax:
            return
        if event.xdata is None:
            return
        if self._dragging:
            self._pan_to(event)
            return
        if self._tracking:
            self._update_annotation(event.xdata, force_draw=True)

    def _on_pan_start(self, event) -> None:
        if self._ax is None or event.inaxes != self._ax:
            return
        if event.button != 3 or event.xdata is None:
            return
        self._tracking = False
        self._dragging = True
        self._press_x = event.xdata
        self._press_y = event.ydata if event.ydata is not None else 0.0
        self._press_xlim = self._ax.get_xlim()
        self._press_ylim = self._ax.get_ylim()

    def _on_pan_end(self, _event) -> None:
        self._dragging = False
        self._press_xlim = None
        self._press_ylim = None

    def _on_track_end(self, event) -> None:
        if event.button == 1:
            self._tracking = False

    def _pan_to(self, event) -> None:
        if not self._dragging or self._ax is None or self._press_xlim is None:
            return
        if event.xdata is None:
            return
        dx = event.xdata - self._press_x
        dy = (event.ydata - self._press_y) if event.ydata is not None else 0.0

        new_left = self._press_xlim[0] - dx
        new_right = self._press_xlim[1] - dx

        new_bottom, new_top = self._ax.get_ylim()
        if self._press_ylim is not None and self._is_shift_pressed(event):
            new_bottom = self._press_ylim[0] - dy
            new_top = self._press_ylim[1] - dy

        if self._base_xlim:
            base_left, base_right = self._base_xlim
            span = new_right - new_left
            if new_left < base_left:
                new_left = base_left
                new_right = base_left + span
            if new_right > base_right:
                new_right = base_right
                new_left = base_right - span

        if self._base_ylim and self._press_ylim is not None and self._is_shift_pressed(event):
            base_bottom, base_top = self._base_ylim
            y_span = new_top - new_bottom
            if new_bottom < base_bottom:
                new_bottom = base_bottom
                new_top = base_bottom + y_span
            if new_top > base_top:
                new_top = base_top
                new_bottom = base_top - y_span

        self._ax.set_xlim(new_left, new_right)
        if self._press_ylim is not None and self._is_shift_pressed(event):
            self._ax.set_ylim(new_bottom, new_top)
        self.canvas.draw_idle()

    def _update_annotation(self, xdata: float, peek: bool = False, force_draw: bool = False) -> None:
        if not self._times_num or not self._values or self._annotation is None:
            return
        index = min(
            range(len(self._times_num)),
            key=lambda i: abs(self._times_num[i] - xdata),
        )
        nearest_x = self._times_num[index]
        nearest_y = self._values[index]
        dt = mdates.num2date(nearest_x)
        message = f"{dt:%Y-%m-%d %H:%M:%S}\n값: {nearest_y:.2f}"
        self._annotation.xy = (nearest_x, nearest_y)
        self._annotation.set_text(message)
        if not self._annotation.get_visible():
            self._annotation.set_visible(True)
        if self._vline is not None and self._hline is not None and self._point is not None:
            self._vline.set_xdata([nearest_x])
            self._hline.set_ydata([nearest_y])
            self._point.set_offsets([[nearest_x, nearest_y]])
            self._vline.set_visible(True)
            self._hline.set_visible(True)
        if not peek or force_draw:
            self.canvas.draw_idle()

    def _is_ctrl_pressed(self, event) -> bool:
        gui_event = getattr(event, "guiEvent", None)
        if gui_event is None:
            return event.key in {"control", "ctrl"}
        return bool(gui_event.modifiers() & Qt.KeyboardModifier.ControlModifier)

    def _is_shift_pressed(self, event) -> bool:
        gui_event = getattr(event, "guiEvent", None)
        if gui_event is None:
            return event.key in {"shift"}
        return bool(gui_event.modifiers() & Qt.KeyboardModifier.ShiftModifier)

    def _reset_view(self) -> None:
        if self._ax is None or self._base_xlim is None or self._base_ylim is None:
            return
        self._ax.set_xlim(*self._base_xlim)
        self._ax.set_ylim(*self._base_ylim)
        self.canvas.draw_idle()

    def _get_zoom_scale(self, event) -> float:
        delta = self._get_scroll_delta(event)
        if delta > 0:
            return 0.9
        if delta < 0:
            return 1.1
        return 1.0

    def _get_scroll_delta(self, event) -> int:
        gui_event = getattr(event, "guiEvent", None)
        if gui_event is not None:
            return int(gui_event.angleDelta().y())
        step = getattr(event, "step", 0)
        return int(step)


class ChartsPanel(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        self.rate_chart = ChartWidget("점적 속도")
        self.cumulative_chart = ChartWidget("누적 점적")
        layout.addWidget(self.rate_chart)
        layout.addWidget(self.cumulative_chart)

    def update_charts(self, logs: list[Log]) -> None:
        self.rate_chart.plot_rate(logs)
        self.cumulative_chart.plot_cumulative(logs)
