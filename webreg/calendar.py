import re
from datetime import datetime, timedelta, date
from typing import List, Dict


HOLIDAYS = {
    date(2026, 1, 19),  # MLK Day
    date(2026, 2, 16),  # Presidents’ Day
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


EXAM_RE = re.compile(
    r"(Midterm|Final\s+Exam).+?(\d{2}/\d{2}/\d{4})\s+(\d+:\d+[ap]-\d+:\d+[ap])\s+([A-Z0-9]+)\s+([A-Z0-9]+)"
)


def parse_time(t: str) -> datetime:
    t = t[:-1] + ("AM" if t.endswith("a") else "PM")
    return datetime.strptime(t, "%I:%M%p")


def parse_time_range(time_str):
    start, end = time_str.split("-")
    return parse_time(start), parse_time(end)


def weekday_indices(days: str) -> List[int]:
    i, out = 0, []
    while i < len(days):
        if days[i:i+2] in DAY_MAP:
            out.append(DAY_MAP[days[i:i+2]])
            i += 2
        else:
            out.append(DAY_MAP[days[i]])
            i += 1
    return out


def generate_ics(lectures: List[Dict], raw_text: str) -> str:
    """
    Generate ICS calendar text from lecture data and raw OCR text.
    """
    events = []

    def event(block: str) -> None:
        events.append(block)

    for row in lectures:
        course = f"{row['subject']} {row['number']}"
        title = f"{course} Lecture"
        location = f"{row['building']} {row['room']}"

        start_t, end_t = parse_time_range(row["time"])

        for wd in weekday_indices(row["days"]):
            first = QUARTER_START + timedelta((wd - QUARTER_START.weekday()) % 7)
            start_dt = datetime.combine(first, start_t.time())
            end_dt = datetime.combine(first, end_t.time())

            exdates = [
                datetime.combine(d, start_t.time())
                for d in HOLIDAYS
                if d.weekday() == wd
            ]

            ex = ""
            if exdates:
                ex = "EXDATE:" + ",".join(
                    d.strftime("%Y%m%dT%H%M%S") for d in exdates
                ) + "\n"

            event(f"""BEGIN:VEVENT
UID:{course}-{wd}@webreg
DTSTAMP:{datetime.now().strftime('%Y%m%dT%H%M%S')}
DTSTART:{start_dt.strftime('%Y%m%dT%H%M%S')}
DTEND:{end_dt.strftime('%Y%m%dT%H%M%S')}
RRULE:FREQ=WEEKLY;UNTIL={QUARTER_END.strftime('%Y%m%dT235959')}
{ex}SUMMARY:{title}
LOCATION:{location}
END:VEVENT
""")

    current_course = None
    for line in raw_text.splitlines():
        if re.match(r"^[A-Z]{2,4}\s+\d+", line):
            parts = line.split()
            current_course = f"{parts[0]} {parts[1]}"

        m = EXAM_RE.search(line)
        if m and current_course:
            kind, date_str, time_str, bldg, room = m.groups()
            start_t, end_t = parse_time_range(time_str)
            exam_date = datetime.strptime(date_str, "%m/%d/%Y").date()

            event(f"""BEGIN:VEVENT
UID:{current_course}-{kind}@webreg
DTSTAMP:{datetime.now().strftime('%Y%m%dT%H%M%S')}
DTSTART:{datetime.combine(exam_date, start_t.time()).strftime('%Y%m%dT%H%M%S')}
DTEND:{datetime.combine(exam_date, end_t.time()).strftime('%Y%m%dT%H%M%S')}
SUMMARY:{current_course} {kind.replace(" Exam","")}
LOCATION:{bldg} {room}
END:VEVENT
""")

    return (
        "BEGIN:VCALENDAR\nVERSION:2.0\nCALSCALE:GREGORIAN\n"
        + "".join(events)
        + "END:VCALENDAR\n"
    )
