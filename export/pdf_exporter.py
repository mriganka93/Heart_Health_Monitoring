# ============================================================
# PDF EXPORTER
# ============================================================

from datetime import datetime
from tkinter import filedialog

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def export_pdf(data, export_columns, parent=None):
    """
    Export health data to a PDF file.

    Parameters
    ----------
    data : list
        Rows of data to export.

    export_columns : list
        Column names selected by the user.

    parent : tkinter widget, optional
        Parent window for the save dialog.

    Returns
    -------
    bool
        True if the PDF was exported successfully.
        False if the user cancelled or an error occurred.
    """

    # ========================================================
    # DEFAULT FILE NAME
    # ========================================================

    filename = datetime.now().strftime(
        "health_data_%Y%m%d_%H%M%S.pdf"
    )

    # ========================================================
    # SAVE FILE DIALOG
    # ========================================================

    filepath = filedialog.asksaveasfilename(
        parent=parent,
        title="Export Health Data to PDF",
        defaultextension=".pdf",
        initialfile=filename,
        filetypes=[
            (
                "PDF files",
                "*.pdf"
            ),
            (
                "All files",
                "*.*"
            ),
        ],
    )

    # User cancelled the dialog
    if not filepath:
        return False

    try:
        # ====================================================
        # CREATE PDF DOCUMENT
        # ====================================================

        document = SimpleDocTemplate(
            filepath,
            pagesize=landscape(A4),
            rightMargin=25,
            leftMargin=25,
            topMargin=25,
            bottomMargin=25,
        )

        # ====================================================
        # STYLES
        # ====================================================

        styles = getSampleStyleSheet()

        # ====================================================
        # TITLE
        # ====================================================

        title = Paragraph(
            "Heart Health Monitor",
            styles["Title"],
        )

        # ====================================================
        # SUBTITLE
        # ====================================================

        subtitle = Paragraph(
            (
                "Health Data Export — "
                f"{datetime.now().strftime('%d %B %Y, %I:%M %p')}"
            ),
            styles["Normal"],
        )

        # ====================================================
        # TABLE HEADER STYLE
        # ====================================================

        header_style = styles["Normal"].clone(
            "ExportHeaderStyle"
        )

        header_style.fontName = "Helvetica-Bold"
        header_style.fontSize = 7
        header_style.textColor = colors.white
        header_style.alignment = 1
        header_style.leading = 9

        # ====================================================
        # TABLE DATA STYLE
        # ====================================================

        data_style = styles["Normal"].clone(
            "ExportDataStyle"
        )

        data_style.fontName = "Helvetica"
        data_style.fontSize = 7
        data_style.textColor = colors.HexColor(
            "#172033"
        )
        data_style.alignment = 1
        data_style.leading = 9

        # ====================================================
        # PREPARE TABLE DATA
        # ====================================================

        table_data = []

        # ----------------------------------------------------
        # HEADER ROW
        # ----------------------------------------------------

        header_row = [
            Paragraph(
                str(column_name),
                header_style,
            )
            for column_name in export_columns
        ]

        table_data.append(header_row)

        # ----------------------------------------------------
        # DATA ROWS
        # ----------------------------------------------------

        for row in data:
            formatted_row = [
                Paragraph(
                    str(value),
                    data_style,
                )
                for value in row
            ]

            table_data.append(formatted_row)

        # ====================================================
        # CREATE TABLE
        # ====================================================

        table = Table(
            table_data,
            repeatRows=1,
        )

        # ====================================================
        # TABLE STYLE
        # ====================================================

        table.setStyle(
            TableStyle(
                [
                    # ----------------------------------------
                    # HEADER BACKGROUND
                    # ----------------------------------------

                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor("#0F172A"),
                    ),

                    # ----------------------------------------
                    # HEADER TEXT
                    # ----------------------------------------

                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (-1, 0),
                        colors.white,
                    ),

                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),

                    (
                        "FONTSIZE",
                        (0, 0),
                        (-1, 0),
                        7,
                    ),

                    # ----------------------------------------
                    # DATA TEXT
                    # ----------------------------------------

                    (
                        "TEXTCOLOR",
                        (0, 1),
                        (-1, -1),
                        colors.HexColor("#172033"),
                    ),

                    (
                        "FONTNAME",
                        (0, 1),
                        (-1, -1),
                        "Helvetica",
                    ),

                    (
                        "FONTSIZE",
                        (0, 1),
                        (-1, -1),
                        7,
                    ),

                    # ----------------------------------------
                    # ALIGNMENT
                    # ----------------------------------------

                    (
                        "ALIGN",
                        (0, 0),
                        (-1, -1),
                        "CENTER",
                    ),

                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "MIDDLE",
                    ),

                    # ----------------------------------------
                    # TABLE GRID
                    # ----------------------------------------

                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.HexColor("#CBD5E1"),
                    ),

                    # ----------------------------------------
                    # ALTERNATING ROW COLORS
                    # ----------------------------------------

                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [
                            colors.white,
                            colors.HexColor("#F8FAFC"),
                        ],
                    ),

                    # ----------------------------------------
                    # CELL PADDING
                    # ----------------------------------------

                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),

                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),

                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        5,
                    ),

                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        5,
                    ),
                ]
            )
        )

        # ====================================================
        # BUILD PDF
        # ====================================================

        document.build(
            [
                title,
                Spacer(1, 8),
                subtitle,
                Spacer(1, 15),
                table,
            ]
        )

        return True

    except Exception as error:
        print(
            "PDF export error:",
            error,
        )

        return False