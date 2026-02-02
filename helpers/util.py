from datetime import datetime

def parse_type(str):
    match str:
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

def parse_days(str):
    temp = []
    if "M" in str:
        temp.append("MO")
    if "Tu" in str:
        temp.append("TU")
    if "W" in str:
        temp.append("WE")
    if "Th" in str:
        temp.append("TH")
    if "F" in str:
        temp.append("FR")
    seperator = ","
    return seperator.join(temp)

def parse_time(str, QUARTER_START, QUARTER_END):
    str = str.replace("a", "AM")
    str = str.replace("p", "PM")
    start_str, end_str = str.split("-")
    temp_start = (datetime.strptime(start_str.strip(), "%I:%M%p").time()).strftime("%H%M%S")
    temp_end = (datetime.strptime(end_str.strip(), "%I:%M%p").time()).strftime("%H%M%S")
    start_time = "{qs}T{time}".format(qs=QUARTER_START, time=temp_start)
    end_time = "{qs}T{time}".format(qs=QUARTER_END, time=temp_end)
    return start_time, end_time