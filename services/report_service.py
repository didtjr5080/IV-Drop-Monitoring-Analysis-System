from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

from matplotlib import rcParams
from matplotlib import dates as mdates
from matplotlib.figure import Figure
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from models.log import Log
from models.patient import Patient
from models.session import Session
from services.analysis_service import AnalysisResult


@dataclass(frozen=True)
class SessionReport:
    session: Session
    analysis: AnalysisResult
    logs: list[Log]


def export_patient_report(
    patient: Patient,
    session_reports: list[SessionReport],
    output_path: str,
) -> None:
    font_name = _register_font()
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        name="Title",
        parent=styles["Heading1"],
        fontName=font_name,
        fontSize=18,
        spaceAfter=10,
    )
    section_style = ParagraphStyle(
        name="Section",
        parent=styles["Heading2"],
        fontName=font_name,
        fontSize=13,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        name="Body",
        parent=styles["BodyText"],
        fontName=font_name,
        fontSize=10,
        leading=14,
    )

    doc = SimpleDocTemplate(output_path, pagesize=A4, rightMargin=36, leftMargin=36)
    story = []

    story.append(Paragraph("수액 점적 모니터링 리포트", title_style))
    story.append(
        Paragraph(
            f"환자: {patient.name} ({patient.patient_id})  /  병상: {patient.bed_number}",
            body_style,
        )
    )
    story.append(Spacer(1, 12))

    for report in session_reports:
        story.append(Paragraph(f"세션 {report.session.session_id}", section_style))
        story.append(_build_session_table(report, font_name))
        story.append(Spacer(1, 10))
        story.append(_build_analysis_table(report, font_name))
        story.append(Spacer(1, 10))
        story.append(Paragraph("그래프", section_style))
        story.extend(_build_charts(report))
        story.append(Spacer(1, 8))
        story.append(Paragraph("로그", section_style))
        story.append(_build_logs_table(report, font_name))
        story.append(Spacer(1, 12))

    doc.build(story)


def _build_session_table(report: SessionReport, font_name: str) -> Table:
    session = report.session
    data = [
        ["시작", _format_dt(session.start_time)],
        ["종료", _format_dt(session.end_time)],
        ["총 점적", str(session.total_drops)],
        ["평균 속도", f"{session.avg_rate:.1f}"],
        ["WARNING", str(session.warning_count)],
        ["ALERT", str(session.alert_count)],
    ]
    table = Table(data, colWidths=[90, 380])
    table.setStyle(_table_style(font_name))
    return table


def _build_analysis_table(report: SessionReport, font_name: str) -> Table:
    analysis = report.analysis
    data = [
        ["분석", "값"],
        ["평균 속도", f"{analysis.avg_rate:.1f}"],
        ["최대 속도", f"{analysis.max_rate:.1f}"],
        ["최소 속도", f"{analysis.min_rate:.1f}"],
        ["WARNING", str(analysis.warning_count)],
        ["ALERT", str(analysis.alert_count)],
        ["안정성 점수", str(analysis.stability_score)],
        ["추세", analysis.trend],
    ]
    table = Table(data, colWidths=[120, 350])
    table.setStyle(_table_style(font_name, header=True))
    return table


def _table_style(font_name: str, header: bool = False) -> TableStyle:
    style = TableStyle(
        [
            ("FONTNAME", (0, 0), (-1, -1), font_name),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d7dde9")),
        ]
    )
    if header:
        style.add("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef3ff"))
        style.add("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1b1f2a"))
    return style


def _build_logs_table(report: SessionReport, font_name: str) -> Table:
    data = [["시간", "속도", "누적", "상태", "간격(sec)"]]
    for log in report.logs:
        data.append(
            [
                _format_dt(log.timestamp),
                f"{log.rate_per_min:.2f}",
                str(log.drop_count),
                log.status,
                f"{log.last_drop_sec:.2f}",
            ]
        )
    table = Table(data, colWidths=[140, 70, 60, 70, 70], repeatRows=1)
    table.setStyle(_table_style(font_name, header=True))
    return table


def _build_charts(report: SessionReport) -> list[Image]:
    _apply_matplotlib_fonts()
    rate_image = _plot_rate(report.logs)
    cumulative_image = _plot_cumulative(report.logs)
    return [rate_image, Spacer(1, 6), cumulative_image]


def _plot_rate(logs: list[Log]) -> Image:
    fig = Figure(figsize=(6.2, 3.2), tight_layout=True)
    ax = fig.add_subplot(111)
    if logs:
        times = [log.timestamp for log in logs]
        rates = [log.rate_per_min for log in logs]
        ax.plot(times, rates, color="#2d6cdf", linewidth=2, label="Rate/min")
        _plot_markers(ax, logs, rates)
        ax.set_title("시간 대비 점적 속도")
        ax.set_ylabel("drops/min")
        ax.grid(True, alpha=0.3)
        ax.legend(loc="upper right")
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    else:
        ax.text(0.5, 0.5, "데이터 없음", ha="center", va="center")
        ax.set_axis_off()
    return _figure_to_image(fig, 480)


def _plot_cumulative(logs: list[Log]) -> Image:
    fig = Figure(figsize=(6.2, 3.2), tight_layout=True)
    ax = fig.add_subplot(111)
    if logs:
        times = [log.timestamp for log in logs]
        drops = [log.drop_count for log in logs]
        ax.plot(times, drops, color="#13a388", linewidth=2, label="Cumulative")
        _plot_markers(ax, logs, drops)
        ax.set_title("시간 대비 누적 점적 수")
        ax.set_ylabel("drops")
        ax.grid(True, alpha=0.3)
        ax.legend(loc="upper left")
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    else:
        ax.text(0.5, 0.5, "데이터 없음", ha="center", va="center")
        ax.set_axis_off()
    return _figure_to_image(fig, 480)


def _plot_markers(ax, logs: list[Log], values: list[float]) -> None:
    warning_x = [log.timestamp for log in logs if log.status == "WARNING"]
    warning_y = [values[idx] for idx, log in enumerate(logs) if log.status == "WARNING"]
    alert_x = [log.timestamp for log in logs if log.status == "ALERT"]
    alert_y = [values[idx] for idx, log in enumerate(logs) if log.status == "ALERT"]
    if warning_x:
        ax.scatter(warning_x, warning_y, color="#f59f00", s=30, label="WARNING")
    if alert_x:
        ax.scatter(alert_x, alert_y, color="#e03131", s=30, label="ALERT")


def _figure_to_image(fig: Figure, width: int) -> Image:
    buffer = BytesIO()
    fig.savefig(buffer, format="png", dpi=140)
    buffer.seek(0)
    image = Image(buffer)
    image.drawWidth = width
    image.drawHeight = width * 0.55
    return image


def _apply_matplotlib_fonts() -> None:
    rcParams["font.family"] = ["Malgun Gothic", "Noto Sans KR", "Segoe UI"]
    rcParams["axes.unicode_minus"] = False


def _format_dt(value) -> str:
    if value is None:
        return "-"
    return value.strftime("%Y-%m-%d %H:%M:%S")


def _register_font() -> str:
    font_path = Path("C:/Windows/Fonts/malgun.ttf")
    if font_path.exists():
        pdfmetrics.registerFont(TTFont("MalgunGothic", str(font_path)))
        return "MalgunGothic"
    return "Helvetica"
