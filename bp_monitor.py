import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sqlite3
import csv
from datetime import datetime, timedelta


# ============================================================
# APPLICATION CONFIGURATION
# ============================================================

APP_NAME = "Heart Health Monitor"
DB_NAME = "health_data.db"

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 850


# ============================================================
# CUSTOMTKINTER THEME
# ============================================================

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


# ============================================================
# COLORS
# ============================================================

COLORS = {
    "background": "#F3F6FA",
    "card": "#FFFFFF",

    "navy": "#0F172A",

    "blue": "#2563EB",
    "blue_hover": "#1D4ED8",

    "green": "#059669",
    "green_hover": "#047857",

    "red": "#DC2626",
    "red_hover": "#B91C1C",

    "gray": "#64748B",
    "light_gray": "#E2E8F0",

    "input": "#F8FAFC",

    "text": "#172033",
    "muted": "#64748B",

    "success_text": "#047857",
    "error_text": "#B91C1C",

    "table_header": "#0F172A",
    "table_even": "#FFFFFF",
    "table_odd": "#F8FAFC",
}


# ============================================================
# DATABASE
# ============================================================

def create_database():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Create database if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS health_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            systolic INTEGER NOT NULL,
            diastolic INTEGER NOT NULL,
            heart_rate INTEGER NOT NULL DEFAULT 0,
            stress INTEGER NOT NULL,
            meditation INTEGER NOT NULL,
            exercise_duration REAL NOT NULL,
            sleep_duration REAL NOT NULL
        )
    """)

    # --------------------------------------------------------
    # DATABASE MIGRATION
    # --------------------------------------------------------
    # If you already had an older health_data.db without
    # heart_rate, add the new column automatically.
    # --------------------------------------------------------

    cursor.execute("""
        PRAGMA table_info(health_records)
    """)

    columns = [
        row[1]
        for row in cursor.fetchall()
    ]

    if "heart_rate" not in columns:

        cursor.execute("""
            ALTER TABLE health_records
            ADD COLUMN heart_rate INTEGER NOT NULL DEFAULT 0
        """)

    conn.commit()
    conn.close()


# ============================================================
# MAIN APPLICATION
# ============================================================

class HealthMonitor(ctk.CTk):

    def __init__(self):

        super().__init__()

        # ----------------------------------------------------
        # WINDOW
        # ----------------------------------------------------

        self.title(APP_NAME)

        self.geometry(
            f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}"
        )

        self.minsize(
            950,
            700
        )

        self.configure(
            fg_color=COLORS["background"]
        )

        # Maximize window on Linux
        try:
            self.state("zoomed")
        except Exception:
            pass

        # ----------------------------------------------------
        # VARIABLES
        # ----------------------------------------------------

        self.systolic_var = tk.StringVar()
        self.diastolic_var = tk.StringVar()

        self.heart_rate_var = tk.StringVar()

        self.exercise_var = tk.StringVar()
        self.sleep_var = tk.StringVar()

        self.stress_var = tk.BooleanVar(
            value=False
        )

        self.meditation_var = tk.BooleanVar(
            value=False
        )

        # ----------------------------------------------------
        # BUILD UI
        # ----------------------------------------------------

        self.create_header()

        self.create_scroll_area()

        self.create_health_entry_card()

        self.create_recent_data_card()

        # ----------------------------------------------------
        # KEYBOARD SHORTCUTS
        # ----------------------------------------------------

        self.bind(
            "<Control-s>",
            lambda event: self.save_record()
        )

        self.bind(
            "<Escape>",
            lambda event: self.clear_form()
        )

    # ========================================================
    # HEADER
    # ========================================================

    def create_header(self):

        self.header = ctk.CTkFrame(
            self,
            height=95,
            corner_radius=0,
            fg_color=COLORS["navy"]
        )

        self.header.pack(
            fill="x"
        )

        self.header.pack_propagate(False)

        header_inner = ctk.CTkFrame(
            self.header,
            fg_color="transparent"
        )

        header_inner.pack(
            fill="both",
            expand=True,
            padx=45
        )

        # ----------------------------------------------------
        # LOGO
        # ----------------------------------------------------

        logo = ctk.CTkFrame(
            header_inner,
            width=50,
            height=50,
            corner_radius=13,
            fg_color=COLORS["blue"]
        )

        logo.pack(
            side="left",
            pady=22
        )

        logo.pack_propagate(False)

        logo_text = ctk.CTkLabel(
            logo,
            text="♥",
            text_color="white",
            font=(
                "Arial",
                25,
                "bold"
            )
        )

        logo_text.pack(
            expand=True
        )

        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        title_frame = ctk.CTkFrame(
            header_inner,
            fg_color="transparent"
        )

        title_frame.pack(
            side="left",
            padx=17
        )

        title = ctk.CTkLabel(
            title_frame,
            text="Heart Health Monitor",
            text_color="white",
            font=(
                "Segoe UI",
                30,
                "bold"
            )
        )

        title.pack(
            anchor="w"
        )

        subtitle = ctk.CTkLabel(
            title_frame,
            text="Personal Heart Health Tracking By @Mriganka",
            text_color="#94A3B8",
            font=(
                "Segoe UI",
                13
            )
        )

        subtitle.pack(
            anchor="w"
        )

        # ----------------------------------------------------
        # DATE
        # ----------------------------------------------------

        today = datetime.now().strftime(
            "%A, %d %B %Y"
        )

        date_label = ctk.CTkLabel(
            header_inner,
            text=today,
            text_color="#CBD5E1",
            font=(
                "Segoe UI",
                13
            )
        )

        date_label.pack(
            side="right"
        )

    # ========================================================
    # SCROLLABLE MAIN AREA
    # ========================================================

    def create_scroll_area(self):

        self.scroll_area = ctk.CTkScrollableFrame(
            self,
            fg_color=COLORS["background"],
            scrollbar_button_color="#CBD5E1",
            scrollbar_button_hover_color="#94A3B8"
        )

        self.scroll_area.pack(
            fill="both",
            expand=True
        )

        self.scroll_area.grid_columnconfigure(
            0,
            weight=1
        )

    # ========================================================
    # HEALTH ENTRY CARD
    # ========================================================

    def create_health_entry_card(self):

        card = ctk.CTkFrame(
            self.scroll_area,
            fg_color=COLORS["card"],
            corner_radius=18,
            border_width=1,
            border_color=COLORS["light_gray"]
        )

        card.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=65,
            pady=(35, 20)
        )

        card.grid_columnconfigure(
            0,
            weight=1
        )

        # ----------------------------------------------------
        # HEADING
        # ----------------------------------------------------

        heading = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )

        heading.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=35,
            pady=(30, 5)
        )

        title = ctk.CTkLabel(
            heading,
            text="Daily Health Entry",
            text_color=COLORS["text"],
            font=(
                "Segoe UI",
                25,
                "bold"
            )
        )

        title.pack(
            side="left"
        )

        badge = ctk.CTkLabel(
            heading,
            text="  TODAY  ",
            text_color="#1D4ED8",
            fg_color="#DBEAFE",
            corner_radius=6,
            font=(
                "Segoe UI",
                11,
                "bold"
            )
        )

        badge.pack(
            side="left",
            padx=14
        )

        # ----------------------------------------------------
        # DESCRIPTION
        # ----------------------------------------------------

        description = ctk.CTkLabel(
            card,
            text=(
                "Record your blood pressure, heart rate, "
                "activity, sleep and daily wellness."
            ),
            text_color=COLORS["muted"],
            font=(
                "Segoe UI",
                15,
                "bold"
            )
        )

        description.grid(
            row=1,
            column=0,
            sticky="w",
            padx=35,
            pady=(0, 25)
        )

        # ----------------------------------------------------
        # INPUT GRID
        # ----------------------------------------------------

        inputs = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )

        inputs.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=28
        )

        inputs.grid_columnconfigure(
            0,
            weight=1
        )

        inputs.grid_columnconfigure(
            1,
            weight=1
        )

        # ----------------------------------------------------
        # SYSTOLIC
        # ----------------------------------------------------

        self.create_input(
            inputs,
            "Systolic Pressure",
            "mmHg",
            "e.g. 120",
            self.systolic_var,
            0,
            0
        )

        # ----------------------------------------------------
        # DIASTOLIC
        # ----------------------------------------------------

        self.create_input(
            inputs,
            "Diastolic Pressure",
            "mmHg",
            "e.g. 80",
            self.diastolic_var,
            0,
            1
        )

        # ----------------------------------------------------
        # HEART RATE
        # ----------------------------------------------------

        self.create_input(
            inputs,
            "Heart Rate",
            "BPM",
            "e.g. 72",
            self.heart_rate_var,
            1,
            0
        )

        # ----------------------------------------------------
        # EXERCISE
        # ----------------------------------------------------

        self.create_input(
            inputs,
            "Exercise Duration",
            "minutes",
            "e.g. 30",
            self.exercise_var,
            1,
            1
        )

        # ----------------------------------------------------
        # SLEEP
        # ----------------------------------------------------

        self.create_input(
            inputs,
            "Sleep Duration",
            "hours",
            "e.g. 7.5",
            self.sleep_var,
            2,
            0
        )

        # ----------------------------------------------------
        # WELLNESS
        # ----------------------------------------------------

        wellness = ctk.CTkFrame(
            inputs,
            fg_color="#F8FAFC",
            corner_radius=12,
            border_width=1,
            border_color=COLORS["light_gray"]
        )

        wellness.grid(
            row=3,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=7,
            pady=(20, 8)
        )

        wellness.grid_columnconfigure(
            0,
            weight=1
        )

        wellness.grid_columnconfigure(
            1,
            weight=1
        )

        wellness_title = ctk.CTkLabel(
            wellness,
            text="Daily Wellness",
            text_color=COLORS["text"],
            font=(
                "Segoe UI",
                15,
                "bold"
            )
        )

        wellness_title.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="w",
            padx=18,
            pady=(15, 10)
        )

        # ----------------------------------------------------
        # STRESS
        # ----------------------------------------------------

        stress_box = ctk.CTkCheckBox(
            wellness,
            text="Stress",
            variable=self.stress_var,
            text_color=COLORS["text"],
            hover_color=COLORS["blue_hover"],
            fg_color=COLORS["blue"],
            border_color="#94A3B8",
            corner_radius=5,
            checkbox_width=24,
            checkbox_height=24,
            font=(
                "Segoe UI",
                14
            )
        )

        stress_box.grid(
            row=1,
            column=0,
            sticky="w",
            padx=18,
            pady=(2, 19)
        )

        # ----------------------------------------------------
        # MEDITATION
        # ----------------------------------------------------

        meditation_box = ctk.CTkCheckBox(
            wellness,
            text="Meditation",
            variable=self.meditation_var,
            text_color=COLORS["text"],
            hover_color=COLORS["blue_hover"],
            fg_color=COLORS["blue"],
            border_color="#94A3B8",
            corner_radius=5,
            checkbox_width=24,
            checkbox_height=24,
            font=(
                "Segoe UI",
                14
            )
        )

        meditation_box.grid(
            row=1,
            column=1,
            sticky="w",
            padx=18,
            pady=(2, 19)
        )

        # ----------------------------------------------------
        # BUTTON BAR
        # ----------------------------------------------------

        buttons = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )

        buttons.grid(
            row=3,
            column=0,
            sticky="ew",
            padx=35,
            pady=(22, 10)
        )

        # ----------------------------------------------------
        # SAVE
        # ----------------------------------------------------

        save_button = ctk.CTkButton(
            buttons,
            text="Save Health Data",
            command=self.save_record,
            width=180,
            height=46,
            corner_radius=9,
            fg_color=COLORS["blue"],
            hover_color=COLORS["blue_hover"],
            font=(
                "Segoe UI",
                14,
                "bold"
            )
        )

        save_button.pack(
            side="right"
        )

        # ----------------------------------------------------
        # CLEAR
        # ----------------------------------------------------

        clear_button = ctk.CTkButton(
            buttons,
            text="Clear",
            command=self.clear_form,
            width=105,
            height=46,
            corner_radius=9,
            fg_color="#64748B",
            hover_color="#475569",
            font=(
                "Segoe UI",
                14,
                "bold"
            )
        )

        clear_button.pack(
            side="right",
            padx=10
        )

        # ----------------------------------------------------
        # DELETE
        # ----------------------------------------------------

        delete_button = ctk.CTkButton(
            buttons,
            text="Delete Last",
            command=self.delete_last_record,
            width=135,
            height=46,
            corner_radius=9,
            fg_color=COLORS["red"],
            hover_color=COLORS["red_hover"],
            font=(
                "Segoe UI",
                14,
                "bold"
            )
        )

        delete_button.pack(
            side="right"
        )

        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        self.status_frame = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )

        self.status_frame.grid(
            row=4,
            column=0,
            sticky="ew",
            padx=35,
            pady=(0, 25)
        )

        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Ready",
            text_color=COLORS["muted"],
            font=(
                "Segoe UI",
                13
            )
        )

        self.status_label.pack(
            anchor="w"
        )

    # ========================================================
    # INPUT FIELD
    # ========================================================

    def create_input(
        self,
        parent,
        label,
        unit,
        placeholder,
        variable,
        row,
        column
    ):

        frame = ctk.CTkFrame(
            parent,
            fg_color="transparent"
        )

        frame.grid(
            row=row,
            column=column,
            sticky="ew",
            padx=7,
            pady=9
        )

        frame.grid_columnconfigure(
            0,
            weight=1
        )

        # ----------------------------------------------------
        # LABEL ROW
        # ----------------------------------------------------

        label_frame = ctk.CTkFrame(
            frame,
            fg_color="transparent"
        )

        label_frame.grid(
            row=0,
            column=0,
            sticky="ew",
            pady=(0, 7)
        )

        label_widget = ctk.CTkLabel(
            label_frame,
            text=label,
            text_color=COLORS["text"],
            font=(
                "Segoe UI",
                14,
                "bold"
            )
        )

        label_widget.pack(
            side="left"
        )

        unit_widget = ctk.CTkLabel(
            label_frame,
            text=unit,
            text_color=COLORS["muted"],
            font=(
                "Segoe UI",
                12
            )
        )

        unit_widget.pack(
            side="right"
        )

        # ----------------------------------------------------
        # ENTRY
        # ----------------------------------------------------

        entry = ctk.CTkEntry(
            frame,
            textvariable=variable,
            height=50,
            corner_radius=9,
            border_width=1,
            border_color=COLORS["light_gray"],
            fg_color=COLORS["input"],
            text_color=COLORS["text"],
            placeholder_text=placeholder,
            placeholder_text_color="#94A3B8",
            font=(
                "Segoe UI",
                15
            )
        )

        entry.grid(
            row=1,
            column=0,
            sticky="ew"
        )

    # ========================================================
    # RECENT DATA CARD
    # ========================================================

    def create_recent_data_card(self):

        card = ctk.CTkFrame(
            self.scroll_area,
            fg_color=COLORS["card"],
            corner_radius=18,
            border_width=1,
            border_color=COLORS["light_gray"]
        )

        card.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=65,
            pady=(0, 40)
        )

        card.grid_columnconfigure(
            0,
            weight=1
        )

        # ----------------------------------------------------
        # HEADER
        # ----------------------------------------------------

        header = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )

        header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=35,
            pady=(30, 20)
        )

        title = ctk.CTkLabel(
            header,
            text="Recent Health Data",
            text_color=COLORS["text"],
            font=(
                "Segoe UI",
                25,
                "bold"
            )
        )

        title.pack(
            side="left"
        )

        subtitle = ctk.CTkLabel(
            header,
            text="  LAST 5 DAYS  ",
            text_color="#475569",
            fg_color="#F1F5F9",
            corner_radius=6,
            font=(
                "Segoe UI",
                11,
                "bold"
            )
        )

        subtitle.pack(
            side="left",
            padx=14
        )

        # ----------------------------------------------------
        # VIEW BUTTON
        # ----------------------------------------------------

        view_button = ctk.CTkButton(
            header,
            text="View Data",
            command=self.view_data,
            width=135,
            height=42,
            corner_radius=8,
            fg_color=COLORS["blue"],
            hover_color=COLORS["blue_hover"],
            font=(
                "Segoe UI",
                13,
                "bold"
            )
        )

        view_button.pack(
            side="right"
        )

        # ----------------------------------------------------
        # TABLE CONTAINER
        # ----------------------------------------------------

        table_container = ctk.CTkFrame(
            card,
            fg_color="white",
            corner_radius=10,
            border_width=1,
            border_color=COLORS["light_gray"]
        )

        table_container.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=35
        )

        # ----------------------------------------------------
        # TABLE STYLE
        # ----------------------------------------------------

        style = ttk.Style()

        try:
            style.theme_use(
                "clam"
            )
        except Exception:
            pass

        style.configure(
            "Health.Treeview",
            background="white",
            foreground=COLORS["text"],
            fieldbackground="white",
            rowheight=50,
            borderwidth=0,
            font=(
                "Segoe UI",
                12
            )
        )

        style.configure(
            "Health.Treeview.Heading",
            background=COLORS["table_header"],
            foreground="white",
            font=(
                "Segoe UI",
                12,
                "bold"
            ),
            relief="flat",
            padding=12
        )

        style.map(
            "Health.Treeview",
            background=[
                (
                    "selected",
                    "#DBEAFE"
                )
            ],
            foreground=[
                (
                    "selected",
                    COLORS["text"]
                )
            ]
        )

        # ----------------------------------------------------
        # COLUMNS
        # ----------------------------------------------------

        columns = (
            "date",
            "systolic",
            "diastolic",
            "heart_rate",
            "stress",
            "meditation",
            "exercise",
            "sleep"
        )

        self.table = ttk.Treeview(
            table_container,
            columns=columns,
            show="headings",
            height=7,
            style="Health.Treeview"
        )

        headers = {
            "date": "Date / Time",
            "systolic": "Systolic",
            "diastolic": "Diastolic",
            "heart_rate": "Heart Rate",
            "stress": "Stress",
            "meditation": "Meditation",
            "exercise": "Exercise",
            "sleep": "Sleep"
        }

        widths = {
            "date": 190,
            "systolic": 105,
            "diastolic": 105,
            "heart_rate": 120,
            "stress": 90,
            "meditation": 110,
            "exercise": 120,
            "sleep": 110
        }

        for column in columns:

            self.table.heading(
                column,
                text=headers[column]
            )

            self.table.column(
                column,
                width=widths[column],
                minwidth=85,
                anchor="center"
            )

        self.table.pack(
            fill="x",
            expand=True
        )

        self.table.tag_configure(
            "even",
            background=COLORS["table_even"]
        )

        self.table.tag_configure(
            "odd",
            background=COLORS["table_odd"]
        )

        # ----------------------------------------------------
        # TABLE STATUS
        # ----------------------------------------------------

        self.table_status = ctk.CTkLabel(
            card,
            text=(
                "Click View Data to display "
                "your recent health records."
            ),
            text_color=COLORS["muted"],
            font=(
                "Segoe UI",
                13
            )
        )

        self.table_status.grid(
            row=2,
            column=0,
            sticky="w",
            padx=35,
            pady=(12, 0)
        )

        # ----------------------------------------------------
        # EXPORT SECTION
        # ----------------------------------------------------

        export_frame = ctk.CTkFrame(
            card,
            fg_color="#F8FAFC",
            corner_radius=12
        )

        export_frame.grid(
            row=3,
            column=0,
            sticky="ew",
            padx=35,
            pady=(20, 30)
        )

        export_info = ctk.CTkLabel(
            export_frame,
            text=(
                "Export your complete heart health history "
                "to a CSV file."
            ),
            text_color=COLORS["muted"],
            font=(
                "Segoe UI",
                13
            )
        )

        export_info.pack(
            side="left",
            padx=20,
            pady=15
        )

        export_button = ctk.CTkButton(
            export_frame,
            text="Export Data",
            command=self.export_data,
            width=145,
            height=42,
            corner_radius=8,
            fg_color=COLORS["green"],
            hover_color=COLORS["green_hover"],
            font=(
                "Segoe UI",
                13,
                "bold"
            )
        )

        export_button.pack(
            side="right",
            padx=12,
            pady=10
        )

    # ========================================================
    # SAVE RECORD
    # ========================================================

    def save_record(self):

        # ----------------------------------------------------
        # SYSTOLIC
        # ----------------------------------------------------

        try:

            systolic = int(
                self.systolic_var.get()
            )

        except ValueError:

            self.show_error(
                "Please enter a valid systolic pressure."
            )

            return

        # ----------------------------------------------------
        # DIASTOLIC
        # ----------------------------------------------------

        try:

            diastolic = int(
                self.diastolic_var.get()
            )

        except ValueError:

            self.show_error(
                "Please enter a valid diastolic pressure."
            )

            return

        # ----------------------------------------------------
        # HEART RATE
        # ----------------------------------------------------

        try:

            heart_rate = int(
                self.heart_rate_var.get()
            )

        except ValueError:

            self.show_error(
                "Please enter a valid heart rate."
            )

            return

        # ----------------------------------------------------
        # EXERCISE
        # ----------------------------------------------------

        try:

            exercise = float(
                self.exercise_var.get()
            )

        except ValueError:

            self.show_error(
                "Please enter exercise duration in minutes."
            )

            return

        # ----------------------------------------------------
        # SLEEP
        # ----------------------------------------------------

        try:

            sleep = float(
                self.sleep_var.get()
            )

        except ValueError:

            self.show_error(
                "Please enter sleep duration in hours."
            )

            return

        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        if systolic <= 0:

            self.show_error(
                "Systolic pressure must be greater than zero."
            )

            return

        if diastolic <= 0:

            self.show_error(
                "Diastolic pressure must be greater than zero."
            )

            return

        if heart_rate <= 0:

            self.show_error(
                "Heart rate must be greater than zero."
            )

            return

        if exercise < 0:

            self.show_error(
                "Exercise duration cannot be negative."
            )

            return

        if sleep < 0:

            self.show_error(
                "Sleep duration cannot be negative."
            )

            return

        if sleep > 24:

            self.show_error(
                "Sleep duration cannot exceed 24 hours."
            )

            return

        # ----------------------------------------------------
        # FLAGS
        # ----------------------------------------------------

        stress = int(
            self.stress_var.get()
        )

        meditation = int(
            self.meditation_var.get()
        )

        # ----------------------------------------------------
        # SAVE TO SQLITE
        # ----------------------------------------------------

        try:

            conn = sqlite3.connect(
                DB_NAME
            )

            cursor = conn.cursor()

            timestamp = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            cursor.execute("""
                INSERT INTO health_records (
                    timestamp,
                    systolic,
                    diastolic,
                    heart_rate,
                    stress,
                    meditation,
                    exercise_duration,
                    sleep_duration
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                timestamp,
                systolic,
                diastolic,
                heart_rate,
                stress,
                meditation,
                exercise,
                sleep
            ))

            conn.commit()
            conn.close()

        except sqlite3.Error as error:

            print(
                "Database error:",
                error
            )

            self.show_error(
                "Unable to save data to the database."
            )

            return

        # ----------------------------------------------------
        # SUCCESS
        # ----------------------------------------------------

        self.clear_form(
            update_status=False
        )

        self.show_success(
            "Health data saved successfully."
        )

    # ========================================================
    # VIEW DATA
    # ========================================================

    def view_data(self):

        conn = sqlite3.connect(
            DB_NAME
        )

        cursor = conn.cursor()

        # Last 5 calendar days including today

        start_date = (
            datetime.now().date()
            - timedelta(days=4)
        )

        start_datetime = datetime.combine(
            start_date,
            datetime.min.time()
        ).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        cursor.execute("""
            SELECT
                timestamp,
                systolic,
                diastolic,
                heart_rate,
                stress,
                meditation,
                exercise_duration,
                sleep_duration
            FROM health_records
            WHERE timestamp >= ?
            ORDER BY timestamp DESC
        """, (
            start_datetime,
        ))

        records = cursor.fetchall()

        conn.close()

        # ----------------------------------------------------
        # CLEAR TABLE
        # ----------------------------------------------------

        for item in self.table.get_children():

            self.table.delete(
                item
            )

        # ----------------------------------------------------
        # INSERT RECORDS
        # ----------------------------------------------------

        for index, record in enumerate(records):

            (
                timestamp,
                systolic,
                diastolic,
                heart_rate,
                stress,
                meditation,
                exercise,
                sleep
            ) = record

            try:

                date_obj = datetime.strptime(
                    timestamp,
                    "%Y-%m-%d %H:%M:%S"
                )

                display_date = date_obj.strftime(
                    "%d %b %Y  %I:%M %p"
                )

            except ValueError:

                display_date = timestamp

            stress_text = (
                "Yes"
                if stress
                else "No"
            )

            meditation_text = (
                "Yes"
                if meditation
                else "No"
            )

            row_tag = (
                "even"
                if index % 2 == 0
                else "odd"
            )

            self.table.insert(
                "",
                "end",
                values=(
                    display_date,
                    systolic,
                    diastolic,
                    f"{heart_rate} BPM",
                    stress_text,
                    meditation_text,
                    f"{exercise:g} min",
                    f"{sleep:g} hr"
                ),
                tags=(row_tag,)
            )

        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        self.table_status.configure(
            text=(
                f"{len(records)} record(s) "
                "found in the last 5 days."
            )
        )

    # ========================================================
    # DELETE LAST RECORD
    # ========================================================

    def delete_last_record(self):

        conn = sqlite3.connect(
            DB_NAME
        )

        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                id,
                timestamp,
                systolic,
                diastolic,
                heart_rate,
                stress,
                meditation,
                exercise_duration,
                sleep_duration
            FROM health_records
            ORDER BY id DESC
            LIMIT 1
        """)

        record = cursor.fetchone()

        if record is None:

            conn.close()

            self.show_error(
                "There are no saved records to delete."
            )

            return

        (
            record_id,
            timestamp,
            systolic,
            diastolic,
            heart_rate,
            stress,
            meditation,
            exercise,
            sleep
        ) = record

        answer = messagebox.askyesno(
            "Delete Last Record",

            (
                "Are you sure you want to delete "
                "the last saved record?\n\n"
                f"Date: {timestamp}\n"
                f"Systolic: {systolic} mmHg\n"
                f"Diastolic: {diastolic} mmHg\n"
                f"Heart Rate: {heart_rate} BPM\n"
                f"Stress: {'Yes' if stress else 'No'}\n"
                f"Meditation: "
                f"{'Yes' if meditation else 'No'}\n"
                f"Exercise: {exercise:g} minutes\n"
                f"Sleep: {sleep:g} hours"
            ),

            icon="warning"
        )

        if not answer:

            conn.close()

            return

        cursor.execute("""
            DELETE FROM health_records
            WHERE id = ?
        """, (
            record_id,
        ))

        conn.commit()
        conn.close()

        self.show_success(
            "Last saved record deleted."
        )

    # ========================================================
    # EXPORT DATA
    # ========================================================

    def export_data(self):

        conn = sqlite3.connect(
            DB_NAME
        )

        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                timestamp,
                systolic,
                diastolic,
                heart_rate,
                stress,
                meditation,
                exercise_duration,
                sleep_duration
            FROM health_records
            ORDER BY timestamp DESC
        """)

        records = cursor.fetchall()

        conn.close()

        if not records:

            self.show_error(
                "There is no data available to export."
            )

            return

        filename = datetime.now().strftime(
            "health_data_%Y%m%d_%H%M%S.csv"
        )

        filepath = filedialog.asksaveasfilename(
            title="Export Health Data",
            defaultextension=".csv",
            initialfile=filename,
            filetypes=[
                (
                    "CSV files",
                    "*.csv"
                ),
                (
                    "All files",
                    "*.*"
                )
            ]
        )

        if not filepath:

            return

        try:

            with open(
                filepath,
                "w",
                newline="",
                encoding="utf-8"
            ) as file:

                writer = csv.writer(
                    file
                )

                writer.writerow([
                    "Date / Time",
                    "Systolic Pressure",
                    "Diastolic Pressure",
                    "Heart Rate (BPM)",
                    "Stress",
                    "Meditation",
                    "Exercise Duration (minutes)",
                    "Sleep Duration (hours)"
                ])

                for record in records:

                    (
                        timestamp,
                        systolic,
                        diastolic,
                        heart_rate,
                        stress,
                        meditation,
                        exercise,
                        sleep
                    ) = record

                    writer.writerow([
                        timestamp,
                        systolic,
                        diastolic,
                        heart_rate,
                        "Yes" if stress else "No",
                        "Yes" if meditation else "No",
                        exercise,
                        sleep
                    ])

            self.show_success(
                "Heart health data exported successfully."
            )

        except Exception as error:

            print(
                "Export error:",
                error
            )

            self.show_error(
                "Unable to export the data."
            )

    # ========================================================
    # CLEAR FORM
    # ========================================================

    def clear_form(
        self,
        update_status=True
    ):

        self.systolic_var.set("")
        self.diastolic_var.set("")

        self.heart_rate_var.set("")

        self.exercise_var.set("")
        self.sleep_var.set("")

        self.stress_var.set(
            False
        )

        self.meditation_var.set(
            False
        )

        if update_status:

            self.status_label.configure(
                text="Form cleared.",
                text_color=COLORS["muted"]
            )

    # ========================================================
    # SUCCESS MESSAGE
    # ========================================================

    def show_success(
        self,
        message
    ):

        self.status_label.configure(
            text=f"✓  {message}",
            text_color=COLORS["success_text"]
        )

    # ========================================================
    # ERROR MESSAGE
    # ========================================================

    def show_error(
        self,
        message
    ):

        self.status_label.configure(
            text=f"⚠  {message}",
            text_color=COLORS["error_text"]
        )


# ============================================================
# START APPLICATION
# ============================================================

if __name__ == "__main__":

    create_database()

    app = HealthMonitor()

    app.mainloop()