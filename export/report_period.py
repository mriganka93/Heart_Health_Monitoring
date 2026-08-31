import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from datetime import datetime, timedelta
import calendar


class ReportPeriodSelector(ctk.CTkToplevel):

    def __init__(self, parent, callback):
        super().__init__(parent)

        self.parent = parent
        self.callback = callback

        self.title("Select Report Period")
        self.geometry("650x600")
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()

        self.configure(
            fg_color="#F3F6FA"
        )

        # ====================================================
        # VARIABLES
        # ====================================================

        self.period_var = tk.StringVar(
            value="Custom"
        )

        self.start_date_var = tk.StringVar()
        self.end_date_var = tk.StringVar()

        # ====================================================
        # HEADER
        # ====================================================

        header = ctk.CTkFrame(
            self,
            fg_color="#0F172A",
            corner_radius=0
        )

        header.pack(
            fill="x"
        )

        title = ctk.CTkLabel(
            header,
            text="Select Report Period",
            text_color="white",
            font=(
                "Segoe UI",
                22,
                "bold"
            )
        )

        title.pack(
            pady=(20, 5)
        )

        subtitle = ctk.CTkLabel(
            header,
            text="Choose the time range for your report",
            text_color="#CBD5E1",
            font=(
                "Segoe UI",
                12
            )
        )

        subtitle.pack(
            pady=(0, 20)
        )

        # ====================================================
        # CONTENT
        # ====================================================

        content = ctk.CTkFrame(
            self,
            fg_color="white",
            corner_radius=14,
            border_width=1,
            border_color="#E2E8F0"
        )

        content.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=25
        )

        # ====================================================
        # PERIOD LABEL
        # ====================================================

        period_label = ctk.CTkLabel(
            content,
            text="Report Duration",
            text_color="#172033",
            font=(
                "Segoe UI",
                14,
                "bold"
            )
        )

        period_label.pack(
            anchor="w",
            padx=25,
            pady=(25, 8)
        )

        # ====================================================
        # PERIOD MENU
        # ====================================================

        period_menu = ctk.CTkOptionMenu(
            content,
            variable=self.period_var,
            values=[
                "1 Week",
                "1 Month",
                "All",
                "Custom"
            ],
            width=250,
            height=42,
            corner_radius=8,
            fg_color="#2563EB",
            button_color="#2563EB",
            button_hover_color="#1D4ED8",
            dropdown_fg_color="white",
            dropdown_hover_color="#DBEAFE",
            text_color="white",
            font=(
                "Segoe UI",
                13,
                "bold"
            ),
            command=self.period_changed
        )

        period_menu.pack(
            anchor="w",
            padx=25
        )

        # ====================================================
        # CUSTOM DATE AREA
        # ====================================================

        self.custom_frame = ctk.CTkFrame(
            content,
            fg_color="#F8FAFC",
            corner_radius=10,
            border_width=1,
            border_color="#E2E8F0"
        )

        # ====================================================
        # START DATE
        # ====================================================

        start_label = ctk.CTkLabel(
            self.custom_frame,
            text="Start Date",
            text_color="#172033",
            font=(
                "Segoe UI",
                12,
                "bold"
            )
        )

        start_label.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="w",
            padx=15,
            pady=(15, 5)
        )

        self.start_entry = ctk.CTkEntry(
            self.custom_frame,
            textvariable=self.start_date_var,
            width=190,
            height=40,
            corner_radius=8,
            border_width=1,
            border_color="#CBD5E1",
            fg_color="white",
            text_color="#172033",
            placeholder_text="YYYY-MM-DD"
        )

        self.start_entry.grid(
            row=1,
            column=0,
            padx=(15, 5),
            pady=(0, 15)
        )

        start_calendar_button = ctk.CTkButton(
            self.custom_frame,
            text="📅",
            width=45,
            height=40,
            corner_radius=8,
            fg_color="#64748B",
            hover_color="#475569",
            command=lambda: self.open_calendar(
                self.start_date_var,
                "Select Start Date"
            )
        )

        start_calendar_button.grid(
            row=1,
            column=1,
            padx=(0, 15),
            pady=(0, 15)
        )

        # ====================================================
        # END DATE
        # ====================================================

        end_label = ctk.CTkLabel(
            self.custom_frame,
            text="End Date",
            text_color="#172033",
            font=(
                "Segoe UI",
                12,
                "bold"
            )
        )

        end_label.grid(
            row=0,
            column=2,
            columnspan=2,
            sticky="w",
            padx=15,
            pady=(15, 5)
        )

        self.end_entry = ctk.CTkEntry(
            self.custom_frame,
            textvariable=self.end_date_var,
            width=190,
            height=40,
            corner_radius=8,
            border_width=1,
            border_color="#CBD5E1",
            fg_color="white",
            text_color="#172033",
            placeholder_text="YYYY-MM-DD"
        )

        self.end_entry.grid(
            row=1,
            column=2,
            padx=(15, 5),
            pady=(0, 15)
        )

        end_calendar_button = ctk.CTkButton(
            self.custom_frame,
            text="📅",
            width=45,
            height=40,
            corner_radius=8,
            fg_color="#64748B",
            hover_color="#475569",
            command=lambda: self.open_calendar(
                self.end_date_var,
                "Select End Date"
            )
        )

        end_calendar_button.grid(
            row=1,
            column=3,
            padx=(0, 15),
            pady=(0, 15)
        )

        # ====================================================
        # BUTTONS
        # ====================================================

        button_frame = ctk.CTkFrame(
            content,
            fg_color="transparent"
        )

        button_frame.pack(
            fill="x",
            padx=25,
            pady=(25, 20)
        )

        # ----------------------------------------------------
        # CANCEL
        # ----------------------------------------------------

        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            width=110,
            height=42,
            corner_radius=8,
            fg_color="#64748B",
            hover_color="#475569",
            command=self.destroy,
            font=(
                "Segoe UI",
                13,
                "bold"
            )
        )

        cancel_button.pack(
            side="left"
        )

        # ----------------------------------------------------
        # APPLY
        # ----------------------------------------------------

        apply_button = ctk.CTkButton(
            button_frame,
            text="Apply Period",
            width=140,
            height=42,
            corner_radius=8,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            command=self.apply_period,
            font=(
                "Segoe UI",
                13,
                "bold"
            )
        )

        apply_button.pack(
            side="right"
        )

        # ====================================================
        # SHOW CUSTOM FIELDS BY DEFAULT
        # ====================================================

        self.period_changed("Custom")

    # ========================================================
    # PERIOD CHANGED
    # ========================================================

    def period_changed(self, value):

        if value == "Custom":

            self.custom_frame.pack(
                fill="x",
                padx=25,
                pady=(20, 0)
            )

            today = datetime.now().date()

            if not self.start_date_var.get():

                self.start_date_var.set(
                    today.strftime("%Y-%m-%d")
                )

            if not self.end_date_var.get():

                self.end_date_var.set(
                    today.strftime("%Y-%m-%d")
                )

        else:

            self.custom_frame.pack_forget()

    # ========================================================
    # CALENDAR
    # ========================================================

    def open_calendar(
        self,
        target_variable,
        calendar_title
    ):
        """
        Open a calendar for selecting either
        the start date or end date.
        """

        calendar_window = ctk.CTkToplevel(
            self
        )

        calendar_window.title(
            calendar_title
        )

        calendar_window.geometry(
            "380x390"
        )

        calendar_window.resizable(
            False,
            False
        )

        calendar_window.transient(
            self
        )

        calendar_window.grab_set()

        calendar_window.configure(
            fg_color="#F3F6FA"
        )

        # ====================================================
        # GET CURRENT SELECTED DATE
        # ====================================================

        today = datetime.now().date()

        selected_date = None

        try:

            current_value = target_variable.get().strip()

            if current_value:

                selected_date = datetime.strptime(
                    current_value,
                    "%Y-%m-%d"
                ).date()

        except ValueError:

            selected_date = None

        if selected_date:

            selected_year = tk.IntVar(
                value=selected_date.year
            )

            selected_month = tk.IntVar(
                value=selected_date.month
            )

        else:

            selected_year = tk.IntVar(
                value=today.year
            )

            selected_month = tk.IntVar(
                value=today.month
            )

        # ====================================================
        # CALENDAR HEADER
        # ====================================================

        header = ctk.CTkFrame(
            calendar_window,
            fg_color="#0F172A",
            corner_radius=0
        )

        header.pack(
            fill="x"
        )

        # ====================================================
        # HEADER NAVIGATION
        # ====================================================

        navigation = ctk.CTkFrame(
            header,
            fg_color="transparent"
        )

        navigation.pack(
            fill="x",
            padx=15,
            pady=15
        )

        navigation.grid_columnconfigure(
            0,
            weight=1
        )

        navigation.grid_columnconfigure(
            1,
            weight=2
        )

        navigation.grid_columnconfigure(
            2,
            weight=1
        )

        # ----------------------------------------------------
        # PREVIOUS BUTTON
        # ----------------------------------------------------

        previous_button = ctk.CTkButton(
            navigation,
            text="‹",
            width=45,
            height=40,
            corner_radius=8,
            fg_color="#334155",
            hover_color="#475569",
            text_color="white",
            font=(
                "Segoe UI",
                24,
                "bold"
            )
        )

        previous_button.grid(
            row=0,
            column=0,
            sticky="w"
        )

        # ----------------------------------------------------
        # MONTH / YEAR
        # ----------------------------------------------------

        month_label = ctk.CTkLabel(
            navigation,
            text="",
            text_color="white",
            font=(
                "Segoe UI",
                17,
                "bold"
            )
        )

        month_label.grid(
            row=0,
            column=1
        )

        # ----------------------------------------------------
        # NEXT BUTTON
        # ----------------------------------------------------

        next_button = ctk.CTkButton(
            navigation,
            text="›",
            width=45,
            height=40,
            corner_radius=8,
            fg_color="#334155",
            hover_color="#475569",
            text_color="white",
            font=(
                "Segoe UI",
                24,
                "bold"
            )
        )

        next_button.grid(
            row=0,
            column=2,
            sticky="e"
        )

        # ====================================================
        # CALENDAR BODY
        # ====================================================

        calendar_frame = ctk.CTkFrame(
            calendar_window,
            fg_color="white",
            corner_radius=12,
            border_width=1,
            border_color="#E2E8F0"
        )

        calendar_frame.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=15
        )

        # ====================================================
        # UPDATE CALENDAR
        # ====================================================

        def update_calendar():

            for widget in calendar_frame.winfo_children():

                widget.destroy()

            year = selected_year.get()
            month = selected_month.get()

            month_name = calendar.month_name[
                month
            ]

            # ------------------------------------------------
            # MONTH / YEAR
            # ------------------------------------------------

            month_label.configure(
                text=f"{month_name} {year}"
            )

            # ------------------------------------------------
            # WEEKDAYS
            # ------------------------------------------------

            weekdays = [
                "Mon",
                "Tue",
                "Wed",
                "Thu",
                "Fri",
                "Sat",
                "Sun"
            ]

            for column, day_name in enumerate(
                weekdays
            ):

                weekday_label = ctk.CTkLabel(
                    calendar_frame,
                    text=day_name,
                    text_color="#64748B",
                    font=(
                        "Segoe UI",
                        11,
                        "bold"
                    )
                )

                weekday_label.grid(
                    row=0,
                    column=column,
                    padx=5,
                    pady=(12, 8)
                )

            # ------------------------------------------------
            # DAYS
            # ------------------------------------------------

            month_calendar = calendar.monthcalendar(
                year,
                month
            )

            for row_index, week in enumerate(
                month_calendar,
                start=1
            ):

                for column_index, day in enumerate(
                    week
                ):

                    if day == 0:
                        continue

                    date_value = datetime(
                        year,
                        month,
                        day
                    ).date()

                    # ------------------------------------------------
                    # TODAY
                    # ------------------------------------------------

                    is_today = (
                        date_value == today
                    )

                    # ------------------------------------------------
                    # SELECTED DATE
                    # ------------------------------------------------

                    is_selected = (
                        selected_date is not None
                        and date_value == selected_date
                    )

                    if is_selected:

                        button_color = "#2563EB"
                        text_color = "white"

                    elif is_today:

                        button_color = "#DBEAFE"
                        text_color = "#1D4ED8"

                    else:

                        button_color = "#F8FAFC"
                        text_color = "#172033"

                    day_button = ctk.CTkButton(
                        calendar_frame,
                        text=str(day),
                        width=38,
                        height=34,
                        corner_radius=7,
                        fg_color=button_color,
                        hover_color="#BFDBFE",
                        text_color=text_color,
                        font=(
                            "Segoe UI",
                            11,
                            "bold"
                        ),
                        command=lambda d=date_value:
                            select_date(d)
                    )

                    day_button.grid(
                        row=row_index,
                        column=column_index,
                        padx=3,
                        pady=3
                    )

        # ====================================================
        # PREVIOUS MONTH
        # ====================================================

        def previous_month():

            month = selected_month.get()
            year = selected_year.get()

            if month == 1:

                selected_month.set(12)
                selected_year.set(
                    year - 1
                )

            else:

                selected_month.set(
                    month - 1
                )

            update_calendar()

        # ====================================================
        # NEXT MONTH
        # ====================================================

        def next_month():

            month = selected_month.get()
            year = selected_year.get()

            if month == 12:

                selected_month.set(1)
                selected_year.set(
                    year + 1
                )

            else:

                selected_month.set(
                    month + 1
                )

            update_calendar()

        # ====================================================
        # SELECT DATE
        # ====================================================

        def select_date(date_value):

            target_variable.set(
                date_value.strftime(
                    "%Y-%m-%d"
                )
            )

            calendar_window.destroy()

        # ====================================================
        # CONNECT NAVIGATION BUTTONS
        # ====================================================

        previous_button.configure(
            command=previous_month
        )

        next_button.configure(
            command=next_month
        )

        # ====================================================
        # INITIAL CALENDAR
        # ====================================================

        update_calendar()

    # ========================================================
    # APPLY PERIOD
    # ========================================================

    def apply_period(self):

        selected_period = self.period_var.get()

        today = datetime.now().date()

        # ====================================================
        # 1 WEEK
        # ====================================================

        if selected_period == "1 Week":

            start_date = today - timedelta(
                days=6
            )

            end_date = today

        # ====================================================
        # 1 MONTH
        # ====================================================

        elif selected_period == "1 Month":

            start_date = today - timedelta(
                days=29
            )

            end_date = today

        # ====================================================
        # ALL
        # ====================================================

        elif selected_period == "All":

            start_date = None
            end_date = None

        # ====================================================
        # CUSTOM
        # ====================================================

        elif selected_period == "Custom":

            start_text = (
                self.start_date_var.get().strip()
            )

            end_text = (
                self.end_date_var.get().strip()
            )

            # ------------------------------------------------
            # EMPTY DATE
            # ------------------------------------------------

            if not start_text or not end_text:

                messagebox.showwarning(
                    "Missing Date",
                    "Please select both start and end dates.",
                    parent=self
                )

                return

            # ------------------------------------------------
            # DATE FORMAT
            # ------------------------------------------------

            try:

                start_date = datetime.strptime(
                    start_text,
                    "%Y-%m-%d"
                ).date()

                end_date = datetime.strptime(
                    end_text,
                    "%Y-%m-%d"
                ).date()

            except ValueError:

                messagebox.showwarning(
                    "Invalid Date",
                    "Please enter dates in YYYY-MM-DD format.",
                    parent=self
                )

                return

            # ------------------------------------------------
            # DATE RANGE
            # ------------------------------------------------

            if start_date > end_date:

                messagebox.showwarning(
                    "Invalid Date Range",
                    "Start date cannot be after the end date.",
                    parent=self
                )

                return

        else:

            return

        # ====================================================
        # SEND PERIOD BACK TO MAIN APPLICATION
        # ====================================================

        self.callback(
            selected_period,
            start_date,
            end_date
        )

        self.destroy()
