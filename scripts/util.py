from datetime import datetime

def parse_type(s):
    match s:
        case "LE":
            return "Lecture"
        case "LA":
            return "Lab"
        case "FI":
            return "Final"
        case "MI":
            return "Midterm"
        case "DI":
            return "Discussion"
        case _:
            return "Other"

def parse_days(s):
    temp = []
    if "M" in s:
        temp.append("MO")
    if "Tu" in s:
        temp.append("TU")
    if "W" in s:
        temp.append("WE")
    if "Th" in s:
        temp.append("TH")
    if "F" in s:
        temp.append("FR")
    return ",".join(temp)

def parse_time(time_str, date_str):
    """Parse a time range string like '10:00a-10:50a' relative to date_str (YYYYMMDD)."""
    time_str = time_str.replace("a", "AM").replace("p", "PM")
    start_str, end_str = time_str.split("-")
    start_t = datetime.strptime(start_str.strip(), "%I:%M%p").strftime("%H%M%S")
    end_t = datetime.strptime(end_str.strip(), "%I:%M%p").strftime("%H%M%S")
    return f"{date_str}T{start_t}", f"{date_str}T{end_t}"