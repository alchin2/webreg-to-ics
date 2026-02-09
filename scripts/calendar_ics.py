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


def fold_line(line):
    # ICS spec: max 75 octets, but don't break mid-word or mid-field
    if len(line) <= 75:
        return line
    folded = []
    while len(line) > 75:
        # Find last space before 75th char
        split = line.rfind(' ', 0, 75)
        if split == -1:
            split = 75
        folded.append(line[:split])
        line = ' ' + line[split:].lstrip()
    folded.append(line)
    return '\n'.join(folded)


def create_ics(df, output_path="schedule.ics"):
    lines = []

    # Calendar header
    lines.extend([
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Course Schedule//EN",
        "CALSCALE:GREGORIAN",
        "X-WR-TIMEZONE:America/Los_Angeles",
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
            event_lines = [
                "BEGIN:VEVENT",
                f"UID:{uid}",
                f"DTSTAMP:{dtstamp}",
                f"DTSTART;TZID={TZID}:{start_time}",
                f"DTEND;TZID={TZID}:{end_time}",
                fold_line(f"SUMMARY:{code} {ctype}"),
                fold_line(f"LOCATION:{location} {room}"),
                "SEQUENCE:0",
                "STATUS:CONFIRMED",
            ]
            event_lines.append("END:VEVENT")
            lines.extend(event_lines)
        # Lectures, Discussions, Labs: recurring weekly
        elif ctype in ["Lecture", "Discussion", "Lab"]:
            # Parse days to list of weekday codes
            day_map = {"MO": 0, "TU": 1, "WE": 2, "TH": 3, "FR": 4}
            days_list = []
            if "M" in days_str:
                days_list.append("MO")
            if "Tu" in days_str:
                days_list.append("TU")
            if "W" in days_str:
                days_list.append("WE")
            if "Th" in days_str:
                days_list.append("TH")
            if "F" in days_str:
                days_list.append("FR")

            quarter_start_date = datetime.strptime(QUARTER_START, "%Y%m%d").date()
            quarter_end_date = datetime.strptime(QUARTER_END, "%Y%m%d").date()

            for day_code in days_list:
                weekday = day_map[day_code]
                # Find first occurrence of this weekday on or after quarter_start_date
                first_date = quarter_start_date
                while first_date.weekday() != weekday:
                    first_date += timedelta(days=1)
                # RRULE: weekly until quarter_end_date
                event_date_str = first_date.strftime("%Y%m%d")
                start_time, end_time = parse_time(time_str, event_date_str, event_date_str)
                event_lines = [
                    "BEGIN:VEVENT",
                    f"UID:{code}-{idx}-{day_code}@schedule",
                    f"DTSTAMP:{dtstamp}",
                    f"DTSTART;TZID={TZID}:{start_time}",
                    f"DTEND;TZID={TZID}:{end_time}",
                    fold_line(f"SUMMARY:{code} {ctype}"),
                    fold_line(f"LOCATION:{location} {room}"),
                    "SEQUENCE:0",
                    "STATUS:CONFIRMED",
                ]
                if ctype == "Lecture":
                    event_lines.append(fold_line(f"DESCRIPTION:{title} with instructor: {instructor}"))
                # RRULE for weekly recurrence
                event_lines.append(f"RRULE:FREQ=WEEKLY;UNTIL={quarter_end_date.strftime('%Y%m%d')}T235959Z;BYDAY={day_code}")
                # EXDATE for holidays
                for h in HOLIDAYS:
                    if h >= first_date and h <= quarter_end_date and h.weekday() == weekday:
                        exdate = h.strftime("%Y%m%d")
                        event_lines.append(f"EXDATE;TZID={TZID}:{exdate}T000000")
                event_lines.append("END:VEVENT")
                lines.extend(event_lines)
        else:
            # Other types: single event, no RRULE
            days = parse_days(days_str)
            start_time, end_time = parse_time(time_str, QUARTER_START, QUARTER_END)
            event_lines = [
                "BEGIN:VEVENT",
                f"UID:{uid}",
                f"DTSTAMP:{dtstamp}",
                f"DTSTART;TZID={TZID}:{start_time}",
                f"DTEND;TZID={TZID}:{end_time}",
                fold_line(f"SUMMARY:{code} {ctype}"),
                fold_line(f"LOCATION:{location} {room}"),
                "SEQUENCE:0",
                "STATUS:CONFIRMED",
            ]
            event_lines.append("END:VEVENT")
            lines.extend(event_lines)

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
