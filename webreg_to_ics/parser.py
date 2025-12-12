import re
from typing import List, Dict


LECTURE_RE = re.compile(
    r"""
    ^(?P<subject>[A-Z]{2,4})\s+
    (?P<number>\d+[A-Z]?)\s+
    (?P<title>.+?)\s+
    (?P<section>A[0-9O]{2,5})\s+
    LE\s+
    (?P<instructor>.+?)\s+
    L\s+
    (?P<units>\d+\.\d+)\s+
    (?P<days>[A-Za-z]+)\s+
    (?P<time>\S+)\s+
    (?P<building>[A-Z0-9]+)\s+
    (?P<room>[A-Z0-9]+)
    """,
    re.VERBOSE,
)


def normalize_text(text: str) -> List[str]:
    return [
        re.sub(r"\s+", " ", line.strip())
        for line in text.splitlines()
        if line.strip()
    ]


def clean_days(days: str) -> str:
    return days.replace("E", "F")


def clean_section(section: str) -> str:
    rest = re.sub(r"[^0-9O]", "", section[1:]).replace("O", "0")
    return "A" + (rest + "00")[:2]


def clean_title(title: str) -> str:
    return title.replace(" Il", " II").replace("Il", "II")


def parse_lectures(text: str) -> List[Dict]:
    """
    Parse lecture rows from OCR text.
    """
    rows = []

    for line in normalize_text(text):
        match = LECTURE_RE.match(line)
        if not match:
            continue

        row = match.groupdict()
        row["days"] = clean_days(row["days"])
        row["section"] = clean_section(row["section"])
        row["title"] = clean_title(row["title"])

        rows.append(row)

    return rows
