# ❤️ Heart Health Monitor version 1.0

A desktop-based **Heart Health Monitor** built with Python, CustomTkinter, and SQLite. The application allows users to record and manage daily health information such as blood pressure, heart rate, exercise, sleep, stress, and meditation.

## ✨ Features

* 🩺 Record **systolic and diastolic blood pressure**
* ❤️ Track **heart rate (BPM)**
* 🏃 Record **exercise duration**
* 😴 Track **sleep duration**
* 🧘 Track daily **stress and meditation**
* 💾 Store health records locally using **SQLite**
* 📊 View health records from the **last 5 days**
* 🗑️ Delete the most recently saved record
* 📤 Export complete health history to **CSV**
* ⌨️ Keyboard shortcuts:

  * `Ctrl + S` — Save health data
  * `Esc` — Clear the form
* 🎨 Modern graphical interface using **CustomTkinter**
* 🗃️ Automatic SQLite database creation and basic database migration

## 🖥️ Interface

The application provides a clean desktop interface with:

* Daily health data entry
* Wellness tracking
* Recent health records table
* Data export functionality
* Status messages for successful and failed operations

## 🛠️ Technologies Used

| Technology    | Purpose                   |
| ------------- | ------------------------- |
| Python        | Application development   |
| CustomTkinter | Modern GUI                |
| Tkinter       | GUI utilities and widgets |
| SQLite        | Local health-data storage |
| CSV           | Health-data export        |
| Datetime      | Date and time handling    |

## 📁 Project Structure

```text
Heart_Health_Monitor/
│
├── bp_monitor.py       # Main application
├── requirements.txt    # Python dependencies
├── .gitignore          # Files excluded from Git
└── README.md           # Project documentation
```

> `health_data.db` is generated automatically when the application runs and should not be committed to Git because it may contain personal health information.

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/Heart_Health_Monitor.git
cd Heart_Health_Monitor
```

### 2. Create a virtual environment

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

Windows:

```powershell
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
python3 bp_monitor.py
```

On some systems, you may use:

```bash
python bp_monitor.py
```

## 🗄️ Database

The application uses **SQLite** for local data storage.

When the application starts, it automatically creates:

```text
health_data.db
```

The database contains a `health_records` table with information including:

* Timestamp
* Systolic pressure
* Diastolic pressure
* Heart rate
* Stress status
* Meditation status
* Exercise duration
* Sleep duration

The application also performs a basic migration check to add the `heart_rate` column when opening an older database created by a previous version.

## 📊 Viewing Health Data

The **Recent Health Data** section displays records from the last five calendar days, including:

* Date and time
* Systolic pressure
* Diastolic pressure
* Heart rate
* Stress
* Meditation
* Exercise
* Sleep

## 📤 Exporting Data

The application can export the complete health history to a CSV file.

Click:

```text
Export Data
```

and choose where to save the CSV file.

Exported files contain:

```text
Date / Time
Systolic Pressure
Diastolic Pressure
Heart Rate (BPM)
Stress
Meditation
Exercise Duration (minutes)
Sleep Duration (hours)
```

## ⌨️ Keyboard Shortcuts

| Shortcut   | Action           |
| ---------- | ---------------- |
| `Ctrl + S` | Save health data |
| `Esc`      | Clear the form   |

## 🔒 Privacy

This application stores health records **locally** using SQLite.

Because health information can be sensitive:

* Do not commit `health_data.db` to GitHub.
* Do not commit exported health-data CSV files.
* Keep personal health records on a trusted/local device.
* The application is intended for personal tracking and does **not** replace professional medical advice.

The repository's `.gitignore` excludes database and CSV files from Git.

## ⚠️ Important Disclaimer

**Heart Health Monitor is a personal health-tracking application and is not a medical device.**

The information recorded by the application should not be used as a substitute for diagnosis, treatment, or advice from a qualified healthcare professional.

If you have concerns about your blood pressure, heart rate, or other health measurements, consult an appropriate healthcare professional.


## 👨‍💻 Author

**Mriganka Saikia**

Built with Python, CustomTkinter, and SQLite.

---

⭐ If you find this project useful, consider giving the repository a star!
