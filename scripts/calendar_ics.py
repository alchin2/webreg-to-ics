import pandas as pd
from datetime import datetime, timedelta, date
import sys
import os
from scripts.extract_table import extract
from scripts.util import parse_type, parse_days, parse_time

HOLIDAYS = {
    date(2026, 1, 19),  # MLK Day
    date(2026, 2, 16),  # Presidents' Day
}

QUARTER_START = "20260105"
QUARTER_END = "20260313"




def create_ics(df, output_path="schedule.ics"):
    lines = []

    # Calendar header
    lines.extend([
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Course Schedule//EN",
        "CALSCALE:GREGORIAN",
    ])

    TZID = "America/Los_Angeles"

    last_code = ""
    last_instructor = ""
    last_title = "" 
    
    for idx, row in df.iterrows():
        code = ""
        instructor = ""
        title = ""

        if row.iloc[0] != "":
            last_code = row.iloc[0]
            last_instructor = row["Instructor"]
            last_title = row["Title"]

        code = last_code
        instructor = last_instructor
        title = last_title

        if not row["Type"]:
            continue

        ctype = parse_type(str(row["Type"]))
        days_str = str(row["Days"])
        time_str = str(row["Time"])
        location = row["BLDG"]
        room = row["Room"]

        uid = f"{code}-{idx}@schedule"
        dtstamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

        # Finals and Midterms: single event, use date from days column
        if ctype in ["Final", "Midterm"]:
            try:
                _, date_str = days_str.split()
                event_date = datetime.strptime(date_str, "%m/%d/%Y").strftime("%Y%m%d")
            except Exception:
                event_date = QUARTER_END  # fallback

            start_time, end_time = parse_time(time_str, event_date, event_date)
            lines.extend([
                "BEGIN:VEVENT",
                f"UID:{uid}",
                f"DTSTAMP:{dtstamp}",
                f"DTSTART;TZID={TZID}:{start_time}",
                f"DTEND;TZID={TZID}:{end_time}",
                f"SUMMARY:{code} {ctype}",
                f"LOCATION:{location} {room}",
            ])
        # Lectures, Discussions, Labs: recurring weekly
        elif ctype in ["Lecture", "Discussion", "Lab"]:
            days = parse_days(days_str)
            start_time, end_time = parse_time(time_str, QUARTER_START, QUARTER_END)
            event_lines = [
                "BEGIN:VEVENT",
                f"UID:{uid}",
                f"DTSTAMP:{dtstamp}",
                f"DTSTART;TZID={TZID}:{start_time}",
                f"DTEND;TZID={TZID}:{end_time}",
                f"SUMMARY:{code} {ctype}",
                f"LOCATION:{location} {room}",
                f"RRULE:FREQ=WEEKLY;BYDAY={days};UNTIL={QUARTER_END}T235959Z",
            ]
            # Only lectures get a description
            if ctype == "Lecture":
                event_lines.insert(-1, f"DESCRIPTION: {title} with instructor: {instructor}")
            lines.extend(event_lines)
        else:
            # Other types: single event, no RRULE
            days = parse_days(days_str)
            start_time, end_time = parse_time(time_str, QUARTER_START, QUARTER_END)
            lines.extend([
                "BEGIN:VEVENT",
                f"UID:{uid}",
                f"DTSTAMP:{dtstamp}",
                f"DTSTART;TZID={TZID}:{start_time}",
                f"DTEND;TZID={TZID}:{end_time}",
                f"SUMMARY:{code} {ctype}",
                f"LOCATION:{location} {room}",
            ])

        # Exclude holidays
        for h in HOLIDAYS:
            exdate = h.strftime("%Y%m%d")
            lines.append(f"EXDATE;TZID={TZID}:{exdate}T000000")

        lines.append("END:VEVENT")

    # footer
    lines.append("END:VCALENDAR")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def main_from_pdf(input_path, output_path="schedule.ics"):
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Error: file not found: {input_path}")

    try:
        df = extract(input_path)
    except Exception as e:
        raise RuntimeError(f"Error extracting table from PDF: {e}")

    if df.empty:
        raise ValueError("Error: extracted table is empty")

    create_ics(df, output_path)
    return output_path

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python calendar_ics.py <input_pdf>")
        sys.exit(1)

    input_path = sys.argv[1]
    try:
        main_from_pdf(input_path)
        print("ICS file created: schedule.ics")
    except Exception as e:
        print(e)
        sys.exit(1)
