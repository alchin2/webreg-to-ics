import pandas as pd
from datetime import datetime, timedelta, date

HOLIDAYS = {
    date(2026, 1, 19),  # MLK Day
    date(2026, 2, 16),  # Presidents' Day
}

QUARTER_START = date(2026, 1, 5)
QUARTER_END = date(2026, 3, 13)

DAY_MAP = {
    "M": 0,
    "Tu": 1,
    "W": 2,
    "Th": 3,
    "F": 4,
}


def parse_time(t: str) -> datetime:
    t = str(t).strip().lower()
    if not t or t == "tba":
        raise ValueError("Invalid time")

    t = t[:-1] + ("AM" if t.endswith("a") else "PM")
    return datetime.strptime(t, "%I:%M%p")


def parse_time_range(time_str: str):
    start, end = map(str.strip, time_str.split("-"))
    return parse_time(start), parse_time(end)


def weekday_indices(days: str):
    i = 0
    out = []
    while i < len(days):
        if days[i:i + 2] in DAY_MAP:
            out.append(DAY_MAP[days[i:i + 2]])
            i += 2
        elif days[i] in DAY_MAP:
            out.append(DAY_MAP[days[i]])
            i += 1
        else:
            i += 1
    return out


def csv_to_ics(csv_path: str) -> str:
    df = pd.read_csv(csv_path)
    df.columns = [c.replace("\n", " ").strip() for c in df.columns]

    events = []

    def add_event(uid, start, end, summary, location, exdates=""):
        events.append(
            f"""BEGIN:VEVENT
UID:{uid}@webreg
DTSTAMP:{datetime.now().strftime('%Y%m%dT%H%M%S')}
DTSTART:{start}
DTEND:{end}
{exdates}SUMMARY:{summary}
LOCATION:{location}
END:VEVENT
"""
        )

    current_course = None

    for _, row in df.iterrows():
        subject = str(row.get("Subject Course", "")).strip()
        course_type = str(row.get("Type", "")).strip()
        days = str(row.get("Days", "")).strip()
        time = str(row.get("Time", "")).strip()
        bldg = str(row.get("BLDG", "")).strip()
        room = str(row.get("Room", "")).strip()

        if subject:
            current_course = subject

        if not current_course or not time:
            continue

        if course_type in {"LE", "DI", "LA"} and days:
            try:
                start_t, end_t = parse_time_range(time)
            except Exception:
                continue

            for wd in weekday_indices(days):
                first_day = QUARTER_START + timedelta(
                    (wd - QUARTER_START.weekday()) % 7
                )

                start_dt = datetime.combine(first_day, start_t.time())
                end_dt = datetime.combine(first_day, end_t.time())

                exdates = [
                    d.strftime("%Y%m%dT%H%M%S")
                    for d in HOLIDAYS
                    if d.weekday() == wd
                ]
                ex = f"EXDATE:{','.join(exdates)}\n" if exdates else ""

                add_event(
                    f"{current_course}-{wd}",
                    start_dt.strftime("%Y%m%dT%H%M%S"),
                    end_dt.strftime("%Y%m%dT%H%M%S"),
                    f"{current_course} {course_type}",
                    f"{bldg} {room}".strip(),
                    ex,
                )

        elif course_type in {"FI", "MI"} and " " in days:
            try:
                _, date_str = days.split(" ", 1)
                exam_date = datetime.strptime(date_str.strip(), "%m/%d/%Y").date()
                start_t, end_t = parse_time_range(time)

                label = "Final" if course_type == "FI" else "Midterm"

                add_event(
                    f"{current_course}-{course_type}-{exam_date}",
                    datetime.combine(exam_date, start_t.time()).strftime("%Y%m%dT%H%M%S"),
                    datetime.combine(exam_date, end_t.time()).strftime("%Y%m%dT%H%M%S"),
                    f"{current_course} {label}",
                    f"{bldg} {room}".strip(),
                )
            except Exception:
                continue

    return (
        "BEGIN:VCALENDAR\n"
        "VERSION:2.0\n"
        "CALSCALE:GREGORIAN\n"
        + "".join(events)
        + "END:VCALENDAR\n"
    )
