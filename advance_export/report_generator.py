import os
import sqlite3
import tempfile
from collections import defaultdict
from datetime import datetime, timedelta
from tkinter import filedialog, messagebox

import matplotlib

# A non-interactive backend is suitable for PDF generation.
matplotlib.use("Agg")

import matplotlib.dates as mdates
import matplotlib.pyplot as plt

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    Table,
    TableStyle,
)

from .insights_service import (
    PERIOD_DAYS,
    aggregate_blood_pressure,
    fetch_blood_pressure_records,
)


NAVY = colors.HexColor("#0F172A")
BLUE = colors.HexColor("#2563EB")
RED = colors.HexColor("#DC2626")
MUTED = colors.HexColor("#64748B")
LIGHT = colors.HexColor("#F3F6FA")
BORDER = colors.HexColor("#E2E8F0")
GREEN = colors.HexColor("#047857")


# These intervals match the blood-pressure aggregation rules.
GROUP_DAYS = {
    "1 Week": 1,
    "2 Weeks": 2,
    "1 Month": 5,
    "2 Months": 10,
    "3 Months": 15,
}


def _make_chart(points, period, output_path):
    """Create the systolic/diastolic time-series chart."""

    fig, ax = plt.subplots(figsize=(10.5, 4.5))
    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#FFFFFF")

    times = [point["timestamp"] for point in points]
    systolic = [point["systolic"] for point in points]
    diastolic = [point["diastolic"] for point in points]

    ax.plot(
        times,
        systolic,
        color="#DC2626",
        linewidth=2.2,
        marker="o",
        markersize=4.5,
        label="Systolic",
    )

    ax.plot(
        times,
        diastolic,
        color="#2563EB",
        linewidth=2.2,
        marker="o",
        markersize=4.5,
        label="Diastolic",
    )

    ax.set_title(
        "Blood Pressure Trend",
        loc="left",
        fontsize=15,
        fontweight="bold",
        color="#0F172A",
        pad=16,
    )

    ax.set_xlabel("Date / Time", color="#475569", labelpad=10)
    ax.set_ylabel("Pressure (mmHg)", color="#475569", labelpad=10)

    ax.grid(
        True,
        linestyle="--",
        linewidth=0.7,
        alpha=0.35,
        color="#94A3B8",
    )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#CBD5E1")
    ax.spines["bottom"].set_color("#CBD5E1")

    ax.tick_params(axis="both", colors="#64748B", labelsize=9)

    if len(times) > 1:
        locator = mdates.AutoDateLocator(minticks=4, maxticks=8)
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(
            mdates.ConciseDateFormatter(locator)
        )
    else:
        ax.xaxis.set_major_formatter(
            mdates.DateFormatter("%d %b %H:%M")
        )

    ax.legend(
        loc="upper left",
        frameon=False,
        ncol=2,
        fontsize=9,
    )

    fig.tight_layout()
    fig.savefig(
        output_path,
        dpi=200,
        bbox_inches="tight",
        facecolor="white",
    )
    plt.close(fig)


def _make_sleep_bp_chart(db_path, period, start, end, output_path):
    """
    Create a comparison chart with:
    - Green bars: average sleep duration in hours.
    - Red curve: average systolic blood pressure.
    - Blue curve: average diastolic blood pressure.

    All three measurements use the same date groups:
    1 Week  = 1-day averages
    2 Weeks = 2-day averages
    1 Month = 5-day averages
    2 Months = 10-day averages
    3 Months = 15-day averages
    """

    group_days = GROUP_DAYS[period]

    with sqlite3.connect(db_path) as connection:
        cursor = connection.cursor()

        cursor.execute("PRAGMA table_info(health_records)")
        columns = {row[1] for row in cursor.fetchall()}

        if "sleep_duration" not in columns:
            raise ValueError(
                "The health_records table does not contain "
                "a 'sleep_duration' column."
            )

        cursor.execute(
            """
            SELECT timestamp, systolic, diastolic, sleep_duration
            FROM health_records
            WHERE timestamp >= ? AND timestamp <= ?
            ORDER BY timestamp ASC
            """,
            (
                start.strftime("%Y-%m-%d %H:%M:%S"),
                end.strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )

        rows = cursor.fetchall()

    # Collect all measurements within identical date groups.
    groups = defaultdict(
        lambda: {
            "sleep": [],
            "systolic": [],
            "diastolic": [],
        }
    )

    for timestamp, systolic, diastolic, sleep_duration in rows:
        try:
            measured_at = datetime.strptime(
                timestamp, "%Y-%m-%d %H:%M:%S"
            )

            elapsed_days = (
                measured_at.date() - start.date()
            ).days

            if elapsed_days < 0:
                continue

            group_index = elapsed_days // group_days

            group = groups[group_index]

            if systolic is not None:
                value = float(systolic)
                if 0 < value < 400:
                    group["systolic"].append(value)

            if diastolic is not None:
                value = float(diastolic)
                if 0 < value < 300:
                    group["diastolic"].append(value)

            if sleep_duration is not None:
                value = float(sleep_duration)

                # Assumes sleep_duration is stored in hours.
                if 0 <= value <= 24:
                    group["sleep"].append(value)

        except (TypeError, ValueError):
            # Skip invalid timestamps or measurement values.
            continue

    # Calculate averages using the same date groups.
    labels = []
    sleep_values = []
    systolic_values = []
    diastolic_values = []

    for group_index in sorted(groups):
        group = groups[group_index]

        # Only compare groups containing all three measurements.
        if not (
            group["sleep"]
            and group["systolic"]
            and group["diastolic"]
        ):
            continue

        group_start = start + timedelta(
            days=group_index * group_days
        )

        labels.append(group_start.strftime("%d %b"))

        sleep_values.append(
            sum(group["sleep"]) / len(group["sleep"])
        )

        systolic_values.append(
            sum(group["systolic"]) / len(group["systolic"])
        )

        diastolic_values.append(
            sum(group["diastolic"]) / len(group["diastolic"])
        )

    if not labels:
        raise ValueError(
            "No matching sleep and blood-pressure measurements "
            "were found in the same date groups. Please check "
            "that sleep_duration and blood-pressure records "
            "are available for the selected period."
        )

    # Create the chart.
    fig, ax1 = plt.subplots(figsize=(10.5, 4.8))

    fig.patch.set_facecolor("#FFFFFF")
    ax1.set_facecolor("#FFFFFF")

    x = list(range(len(labels)))

    # LEFT AXIS: sleep duration bars.
    ax1.bar(
        x,
        sleep_values,
        width=0.55,
        color="#16A34A",
        alpha=0.55,
        edgecolor="#047857",
        linewidth=0.8,
        label="Average Sleep (hours)",
        zorder=2,
    )

    ax1.set_ylabel(
        "Average Sleep Duration (hours)",
        color="#047857",
        fontsize=10,
        labelpad=10,
    )

    ax1.set_ylim(
        0,
        max(10, max(sleep_values) * 1.25),
    )

    ax1.set_xticks(x)
    ax1.set_xticklabels(
        labels,
        rotation=30,
        ha="right",
    )

    # RIGHT AXIS: blood-pressure curves.
    ax2 = ax1.twinx()

    ax2.plot(
        x,
        systolic_values,
        color="#DC2626",
        linewidth=2.4,
        marker="o",
        markersize=6,
        label="Average Systolic (mmHg)",
        zorder=4,
    )

    ax2.plot(
        x,
        diastolic_values,
        color="#2563EB",
        linewidth=2.4,
        marker="o",
        markersize=6,
        label="Average Diastolic (mmHg)",
        zorder=4,
    )

    ax2.set_ylabel(
        "Average Blood Pressure (mmHg)",
        color="#475569",
        fontsize=10,
        labelpad=10,
    )

    # Chart title.
    ax1.set_title(
        "Average Sleep Duration vs Blood Pressure",
        loc="left",
        fontsize=15,
        fontweight="bold",
        color="#0F172A",
        pad=18,
    )

    # Styling.
    ax1.grid(
        axis="y",
        linestyle="--",
        linewidth=0.7,
        alpha=0.3,
        color="#94A3B8",
        zorder=0,
    )

    ax1.spines["top"].set_visible(False)
    ax2.spines["top"].set_visible(False)

    ax1.spines["left"].set_color("#CBD5E1")
    ax1.spines["bottom"].set_color("#CBD5E1")

    ax1.tick_params(
        axis="both",
        colors="#64748B",
        labelsize=9,
    )

    ax2.tick_params(
        axis="y",
        colors="#64748B",
        labelsize=9,
    )

    # Combine the bar and curve legends.
    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()

    ax1.legend(
        handles1 + handles2,
        labels1 + labels2,
        loc="upper left",
        frameon=False,
        fontsize=8,
        ncol=3,
    )

    fig.tight_layout()

    fig.savefig(
        output_path,
        dpi=200,
        bbox_inches="tight",
        facecolor="white",
    )

    plt.close(fig)


def _build_pdf(
    output_path,
    period,
    start,
    end,
    raw_records,
    points,
    chart_path,
    sleep_chart_path,
):
    """Build the advanced insights PDF."""

    document = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=17 * mm,
        leftMargin=17 * mm,
        topMargin=15 * mm,
        bottomMargin=16 * mm,
        title="Heart Health Monitor - Advanced Insights",
        author="Heart Health Monitor",
    )

    styles = getSampleStyleSheet()

    styles.add(
        ParagraphStyle(
            name="AppTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=21,
            leading=26,
            textColor=colors.white,
            alignment=TA_LEFT,
            spaceAfter=4,
        )
    )

    styles.add(
        ParagraphStyle(
            name="SectionTitle",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=17,
            textColor=NAVY,
            spaceBefore=8,
            spaceAfter=8,
        )
    )

    styles.add(
        ParagraphStyle(
            name="SmallMuted",
            parent=styles["Normal"],
            fontSize=8.5,
            leading=12,
            textColor=MUTED,
        )
    )

    story = []

    # Report header.
    header = Table(
        [[
            Paragraph(
                "♥  Heart Health Monitor by Mriganka",
                styles["AppTitle"],
            ),
            Paragraph(
                "ADVANCED<br/>BLOOD PRESSURE REPORT",
                ParagraphStyle(
                    "HeaderRight",
                    parent=styles["Normal"],
                    fontName="Helvetica-Bold",
                    fontSize=9,
                    leading=13,
                    alignment=2,
                    textColor=colors.white,
                ),
            ),
        ]],
        colWidths=[112 * mm, 62 * mm],
    )

    header.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), NAVY),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ("TOPPADDING", (0, 0), (-1, -1), 14),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
        ])
    )

    story.append(header)
    story.append(Spacer(1, 8 * mm))

    metadata = Table(
        [
            ["REPORT PERIOD", "DATE RANGE", "GENERATED"],
            [
                period,
                f"{start:%d %b %Y} – {end:%d %b %Y}",
                datetime.now().strftime("%d %b %Y, %I:%M %p"),
            ],
        ],
        colWidths=[43 * mm, 75 * mm, 56 * mm],
    )

    metadata.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
            ("TEXTCOLOR", (0, 0), (-1, 0), MUTED),
            ("TEXTCOLOR", (0, 1), (-1, 1), NAVY),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 7.5),
            ("FONTSIZE", (0, 1), (-1, 1), 9),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 9),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LINEBELOW", (0, 0), (-1, 0), 0.5, BORDER),
        ])
    )

    story.append(metadata)
    story.append(Spacer(1, 6 * mm))

    # Blood-pressure trend chart.
    story.append(
        Paragraph("Blood Pressure Trend", styles["SectionTitle"])
    )

    chart = Image(
        chart_path,
        width=176 * mm,
        height=75 * mm,
    )
    chart.hAlign = "CENTER"

    story.append(chart)
    story.append(Spacer(1, 3 * mm))

    # Summary of all raw measurements.
    systolic_values = [r["systolic"] for r in raw_records]
    diastolic_values = [r["diastolic"] for r in raw_records]

    avg_sys = sum(systolic_values) / len(systolic_values)
    avg_dia = sum(diastolic_values) / len(diastolic_values)

    summary = Table(
        [
            [
                "MEASUREMENTS",
                "AVERAGE SYSTOLIC",
                "AVERAGE DIASTOLIC",
            ],
            [
                str(len(raw_records)),
                f"{avg_sys:.1f} mmHg",
                f"{avg_dia:.1f} mmHg",
            ],
        ],
        colWidths=[58 * mm, 58 * mm, 58 * mm],
    )

    summary.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
            ("TEXTCOLOR", (0, 0), (-1, 0), MUTED),
            ("TEXTCOLOR", (0, 1), (0, 1), NAVY),
            ("TEXTCOLOR", (1, 1), (1, 1), RED),
            ("TEXTCOLOR", (2, 1), (2, 1), BLUE),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 7.5),
            ("FONTSIZE", (0, 1), (-1, 1), 12),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER),
        ])
    )

    story.append(summary)
    story.append(Spacer(1, 4 * mm))

    if period == "1 Week":
        method_text = (
            "Blood-pressure chart: individual recorded measurements "
            "in chronological order."
        )
    else:
        method_text = (
            f"Blood-pressure chart: non-overlapping "
            f"{GROUP_DAYS[period]}-day groups. Each point represents "
            "the mean of available measurements in that group."
        )

    story.append(
        Paragraph(method_text, styles["SmallMuted"])
    )
    story.append(Spacer(1, 5 * mm))

    # Sleep and blood-pressure comparison chart.
    story.append(
        Paragraph(
            "Sleep Duration vs Blood Pressure",
            styles["SectionTitle"],
        )
    )

    sleep_chart = Image(
        sleep_chart_path,
        width=176 * mm,
        height=75 * mm,
    )
    sleep_chart.hAlign = "CENTER"

    story.append(sleep_chart)
    story.append(Spacer(1, 3 * mm))

    story.append(
        Paragraph(
            "Green bars represent average sleep duration in hours. "
            "Red and blue bars represent average systolic and "
            "diastolic pressure in mmHg, respectively. Sleep and "
            "blood-pressure values use separate vertical axes "
            "because their units differ. Groups without matching "
            "sleep and blood-pressure measurements are omitted. "
            "This chart shows an association between recorded "
            "measurements; it does not establish causation.",
            styles["SmallMuted"],
        )
    )

    def draw_footer(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(BORDER)
        canvas.line(
            17 * mm,
            12 * mm,
            A4[0] - 17 * mm,
            12 * mm,
        )
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(MUTED)
        canvas.drawString(
            17 * mm,
            7 * mm,
            "Heart Health Monitor",
        )
        canvas.drawRightString(
            A4[0] - 17 * mm,
            7 * mm,
            f"Page {doc.page}",
        )
        canvas.restoreState()

    document.build(
        story,
        onFirstPage=draw_footer,
        onLaterPages=draw_footer,
    )


def export_advanced_insights(parent, db_path, period):
    """Create the advanced insights PDF."""

    if period not in PERIOD_DAYS:
        messagebox.showerror(
            "Invalid Period",
            "Please select 1 Week, 2 Weeks, 1 Month, "
            "2 Months, or 3 Months.",
            parent=parent,
        )
        return False

    raw_records, start, end = fetch_blood_pressure_records(
        db_path,
        period,
    )

    if not raw_records:
        messagebox.showinfo(
            "No Measurements",
            f"No blood-pressure measurements were found for {period}.",
            parent=parent,
        )
        return False

    points = aggregate_blood_pressure(
        raw_records,
        period,
        start,
    )

    default_name = (
        f"Heart_Health_Advanced_Insights_"
        f"{period.replace(' ', '_')}_"
        f"{datetime.now():%Y%m%d}.pdf"
    )

    output_path = filedialog.asksaveasfilename(
        parent=parent,
        title="Save Advanced Insights PDF",
        defaultextension=".pdf",
        initialfile=default_name,
        filetypes=[("PDF document", "*.pdf")],
    )

    if not output_path:
        return False

    if not output_path.lower().endswith(".pdf"):
        output_path += ".pdf"

    chart_path = None
    sleep_chart_path = None

    try:
        # Temporary image for the blood-pressure chart.
        with tempfile.NamedTemporaryFile(
            suffix=".png",
            delete=False,
        ) as temp_chart:
            chart_path = temp_chart.name

        # Temporary image for the sleep/BP comparison chart.
        with tempfile.NamedTemporaryFile(
            suffix=".png",
            delete=False,
        ) as temp_sleep_chart:
            sleep_chart_path = temp_sleep_chart.name

        _make_chart(
            points,
            period,
            chart_path,
        )

        _make_sleep_bp_chart(
            db_path,
            period,
            start,
            end,
            sleep_chart_path,
        )

        _build_pdf(
            output_path,
            period,
            start,
            end,
            raw_records,
            points,
            chart_path,
            sleep_chart_path,
        )

        messagebox.showinfo(
            "Export Successful",
            f"Advanced Insights PDF saved to:\n{output_path}",
            parent=parent,
        )
        return True

    except Exception as error:
        messagebox.showerror(
            "Export Failed",
            f"Unable to create the PDF report.\n\n{error}",
            parent=parent,
        )
        return False

    finally:
        for temporary_path in (chart_path, sleep_chart_path):
            if temporary_path and os.path.exists(temporary_path):
                try:
                    os.remove(temporary_path)
                except OSError:
                    pass