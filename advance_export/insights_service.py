import sqlite3
from datetime import datetime, timedelta


PERIOD_DAYS = {
    "1 Week": 7,
    "2 Weeks": 14,
    "1 Month": 30,
    "2 Months": 60,
    "3 Months": 90,
}

GROUP_DAYS = {
    "1 Week": 1,   # Raw measurements; no averaging
    "2 Weeks": 2,
    "1 Month": 5,
    "2 Months": 10,
    "3 Months": 15,
}


def fetch_blood_pressure_records(db_path, period, now=None):
    """Fetch records in the selected rolling calendar-day period."""

    if period not in PERIOD_DAYS:
        raise ValueError(f"Unsupported report period: {period}")

    now = now or datetime.now()
    start = (now - timedelta(days=PERIOD_DAYS[period] - 1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    end = now

    query = """
        SELECT timestamp, systolic, diastolic
        FROM health_records
        WHERE timestamp >= ? AND timestamp <= ?
        ORDER BY timestamp ASC
    """

    with sqlite3.connect(db_path) as connection:
        rows = connection.execute(
            query,
            (
                start.strftime("%Y-%m-%d %H:%M:%S"),
                end.strftime("%Y-%m-%d %H:%M:%S"),
            ),
        ).fetchall()

    records = []

    for timestamp, systolic, diastolic in rows:
        try:
            measured_at = datetime.strptime(
                timestamp, "%Y-%m-%d %H:%M:%S"
            )
            systolic = float(systolic)
            diastolic = float(diastolic)
        except (TypeError, ValueError):
            # Skip malformed records rather than breaking the report.
            continue

        records.append({
            "timestamp": measured_at,
            "systolic": systolic,
            "diastolic": diastolic,
        })

    return records, start, end


def aggregate_blood_pressure(records, period, start):
    """
    Keep raw readings for one week; otherwise average fixed,
    non-overlapping groups measured from the report start date.
    Empty groups are omitted.
    """

    if period not in GROUP_DAYS:
        raise ValueError(f"Unsupported report period: {period}")

    if period == "1 Week":
        return [
            {
                "timestamp": row["timestamp"],
                "systolic": row["systolic"],
                "diastolic": row["diastolic"],
                "count": 1,
            }
            for row in records
        ]

    group_days = GROUP_DAYS[period]
    groups = {}

    for row in records:
        elapsed_days = (row["timestamp"].date() - start.date()).days
        group_index = max(0, elapsed_days // group_days)
        groups.setdefault(group_index, []).append(row)

    results = []

    for group_index in sorted(groups):
        group = groups[group_index]

        # Plot each group's average at the midpoint of its actual
        # calendar interval, not at the time of an arbitrary reading.
        group_start = start + timedelta(days=group_index * group_days)
        group_end = group_start + timedelta(days=group_days)
        midpoint = group_start + (group_end - group_start) / 2

        results.append({
            "timestamp": midpoint,
            "systolic": sum(r["systolic"] for r in group) / len(group),
            "diastolic": sum(r["diastolic"] for r in group) / len(group),
            "count": len(group),
        })

    return results