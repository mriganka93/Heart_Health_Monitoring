import sqlite3
import random
from datetime import datetime, timedelta

DB_NAME = "health_data.db"


# ============================================================
# DUMMY DATA OPTIONS
# ============================================================

HEART_MEDICATIONS = [
    "Metoprolol",
    "Bisoprolol",
    "Carvedilol",
    "Atorvastatin",
    "Aspirin",
    "None"
]

BP_MEDICATIONS = [
    "Amlodipine",
    "Losartan",
    "Telmisartan",
    "Ramipril",
    "Enalapril",
    "Hydrochlorothiazide",
    "None"
]

DAILY_NOTES = [
    "Feeling good",
    "Feeling energetic",
    "Feeling slightly tired",
    "Feeling dizzy",
    "Mild headache today",
    "Feeling better today",
    "Slept well and feeling good",
    "Feeling a little stressed",
    "No unusual symptoms",
    "Feeling normal today",
    "Had a good day",
    "Feeling tired after exercise",
]


# ============================================================
# CREATE / UPDATE DATABASE
# ============================================================

def setup_database():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS health_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            systolic INTEGER NOT NULL,
            diastolic INTEGER NOT NULL,
            heart_rate INTEGER NOT NULL DEFAULT 0,
            stress INTEGER NOT NULL DEFAULT 0,
            meditation INTEGER NOT NULL DEFAULT 0,
            heart_medication INTEGER NOT NULL DEFAULT 0,
            bp_medication INTEGER NOT NULL DEFAULT 0,
            exercise_duration REAL NOT NULL DEFAULT 0,
            sleep_duration REAL NOT NULL DEFAULT 0
        )
    """)

    # Check existing columns
    cursor.execute("""
        PRAGMA table_info(health_records)
    """)

    columns = [
        row[1]
        for row in cursor.fetchall()
    ]

    # Add newer columns if your database is older
    if "heart_rate" not in columns:
        cursor.execute("""
            ALTER TABLE health_records
            ADD COLUMN heart_rate INTEGER NOT NULL DEFAULT 0
        """)

    if "stress" not in columns:
        cursor.execute("""
            ALTER TABLE health_records
            ADD COLUMN stress INTEGER NOT NULL DEFAULT 0
        """)

    if "meditation" not in columns:
        cursor.execute("""
            ALTER TABLE health_records
            ADD COLUMN meditation INTEGER NOT NULL DEFAULT 0
        """)

    if "heart_medication" not in columns:
        cursor.execute("""
            ALTER TABLE health_records
            ADD COLUMN heart_medication INTEGER NOT NULL DEFAULT 0
        """)

    if "bp_medication" not in columns:
        cursor.execute("""
            ALTER TABLE health_records
            ADD COLUMN bp_medication INTEGER NOT NULL DEFAULT 0
        """)

    if "exercise_duration" not in columns:
        cursor.execute("""
            ALTER TABLE health_records
            ADD COLUMN exercise_duration REAL NOT NULL DEFAULT 0
        """)

    if "sleep_duration" not in columns:
        cursor.execute("""
            ALTER TABLE health_records
            ADD COLUMN sleep_duration REAL NOT NULL DEFAULT 0
        """)

    # --------------------------------------------------------
    # NEW MEDICATION NAME COLUMNS
    # --------------------------------------------------------

    if "heart_medication_name" not in columns:
        cursor.execute("""
            ALTER TABLE health_records
            ADD COLUMN heart_medication_name TEXT DEFAULT ''
        """)

    if "bp_medication_name" not in columns:
        cursor.execute("""
            ALTER TABLE health_records
            ADD COLUMN bp_medication_name TEXT DEFAULT ''
        """)

    # --------------------------------------------------------
    # DAILY NOTE COLUMN
    # --------------------------------------------------------

    if "daily_note" not in columns:
        cursor.execute("""
            ALTER TABLE health_records
            ADD COLUMN daily_note TEXT DEFAULT ''
        """)

    conn.commit()

    return conn


# ============================================================
# GENERATE ONE DUMMY RECORD
# ============================================================

def generate_record(date):

    # --------------------------------------------------------
    # BLOOD PRESSURE
    # --------------------------------------------------------

    systolic = random.randint(
        112,
        138
    )

    diastolic = random.randint(
        70,
        88
    )

    # --------------------------------------------------------
    # HEART RATE
    # --------------------------------------------------------

    heart_rate = random.randint(
        62,
        88
    )

    # --------------------------------------------------------
    # WELLNESS
    # --------------------------------------------------------

    stress = random.choice([
        0,
        0,
        0,
        1
    ])

    meditation = random.choice([
        0,
        0,
        1
    ])

    # --------------------------------------------------------
    # HEART MEDICATION
    # --------------------------------------------------------

    heart_medication = random.choice([
        0,
        1,
        1,
        1
    ])

    if heart_medication:

        heart_medication_name = random.choice(
            HEART_MEDICATIONS[:-1]
        )

    else:

        heart_medication_name = ""

    # --------------------------------------------------------
    # BP MEDICATION
    # --------------------------------------------------------

    bp_medication = random.choice([
        0,
        1,
        1,
        1
    ])

    if bp_medication:

        bp_medication_name = random.choice(
            BP_MEDICATIONS[:-1]
        )

    else:

        bp_medication_name = ""

    # --------------------------------------------------------
    # EXERCISE
    # --------------------------------------------------------

    exercise_duration = random.choice([
        0,
        15,
        20,
        25,
        30,
        35,
        40,
        45,
        50
    ])

    # --------------------------------------------------------
    # SLEEP
    # --------------------------------------------------------

    sleep_duration = round(
        random.uniform(
            5.5,
            8.5
        ),
        1
    )

    # --------------------------------------------------------
    # DAILY NOTE
    # --------------------------------------------------------

    note = random.choice(
        DAILY_NOTES
    )

    # --------------------------------------------------------
    # RANDOM TIME
    # --------------------------------------------------------

    hour = random.randint(
        7,
        10
    )

    minute = random.randint(
        0,
        59
    )

    record_datetime = datetime.combine(
        date,
        datetime.min.time()
    ).replace(
        hour=hour,
        minute=minute,
        second=0
    )

    timestamp = record_datetime.strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    return (
        timestamp,
        systolic,
        diastolic,
        heart_rate,
        stress,
        meditation,
        heart_medication,
        bp_medication,
        exercise_duration,
        sleep_duration,
        heart_medication_name,
        bp_medication_name,
        note
    )


# ============================================================
# INSERT DUMMY DATA
# ============================================================

def insert_dummy_data(
    number_of_days=30
):

    conn = setup_database()

    cursor = conn.cursor()

    print()
    print("=" * 60)
    print("HEART HEALTH MONITOR - DUMMY DATA GENERATOR")
    print("=" * 60)
    print()

    # --------------------------------------------------------
    # GENERATE DATA
    # --------------------------------------------------------

    today = datetime.now().date()

    inserted = 0

    for days_ago in range(
        number_of_days - 1,
        -1,
        -1
    ):

        record_date = (
            today
            - timedelta(days=days_ago)
        )

        record = generate_record(
            record_date
        )

        cursor.execute("""
            INSERT INTO health_records (
                timestamp,
                systolic,
                diastolic,
                heart_rate,
                stress,
                meditation,
                heart_medication,
                bp_medication,
                exercise_duration,
                sleep_duration,
                heart_medication_name,
                bp_medication_name,
                daily_note
            )
            VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?
            )
        """, record)

        inserted += 1

        print(
            f"Added: {record[0]} | "
            f"BP {record[1]}/{record[2]} | "
            f"HR {record[3]} | "
            f"Heart Med: "
            f"{record[10] or 'None'} | "
            f"BP Med: "
            f"{record[11] or 'None'} | "
            f"Note: {record[12]}"
        )

    conn.commit()
    conn.close()

    print()
    print("=" * 60)
    print(
        f"Successfully inserted {inserted} dummy records."
    )
    print("=" * 60)
    print()
    print(
        "Open your Heart Health Monitor application "
        "and click 'View Data'."
    )
    print()


# ============================================================
# OPTIONAL: CLEAR ONLY DUMMY DATA
# ============================================================

def delete_all_records():

    answer = input(
        "Delete ALL records from health_records? "
        "Type YES to continue: "
    )

    if answer != "YES":

        print("Cancelled.")
        return

    conn = sqlite3.connect(
        DB_NAME
    )

    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM health_records
    """)

    conn.commit()
    conn.close()

    print(
        "All health records have been deleted."
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print()
    print("Choose an option:")
    print()
    print("1. Add 30 days of dummy data")
    print("2. Add 60 days of dummy data")
    print("3. Add 90 days of dummy data")
    print("4. Delete all records")
    print("5. Exit")
    print()

    choice = input(
        "Enter your choice: "
    ).strip()

    if choice == "1":

        insert_dummy_data(
            30
        )

    elif choice == "2":

        insert_dummy_data(
            60
        )

    elif choice == "3":

        insert_dummy_data(
            90
        )

    elif choice == "4":

        delete_all_records()

    elif choice == "5":

        print(
            "Exiting..."
        )

    else:

        print(
            "Invalid choice."
        )
