Here is the Markdown content for your README file:

# Course Schedule to ICS Converter

This tool extracts university course schedules from PDF files and converts them into an `.ics` (iCalendar) file. This allows you to easily import your classes, labs, discussions, midterms, and finals into calendar applications like Google Calendar, Apple Calendar, or Microsoft Outlook.

## Features

* **PDF Table Extraction**: Uses `PyMuPDF` to accurately crop and extract schedule tables from PDFs.
* **Intelligent Parsing**: Automatically handles "merged rows" in the PDF (where course info is listed once for multiple time slots).
* **Recurring Events**: Supports weekly recurrence for Lectures (LE), Labs (LA), and Discussions (DI).
* **Exam Support**: Handles single-instance events like Finals (FI) and Midterms (MI) using specific dates parsed from the document.
* **Holiday Exclusion**: Automatically excludes specific dates (like MLK Day or Presidents' Day) from recurring schedules using `EXDATE`.
* **Location Tracking**: Includes building codes and room numbers in the calendar event location.

## Project Structure

To run the script correctly, ensure your files are organized as follows:

```
.
├── calendar_ics.py         # Main entry point
├── requirements.txt        # Project dependencies
└── helpers/                # Logic modules
    ├── extract_table.py    # PDF extraction logic
    └── util.py             # Parsing and formatting utilities

```

## Installation

1. **Clone the repository** (or download the source files).
2. **Install dependencies**:
It is recommended to use a virtual environment.
```bash
pip install -r requirements.txt

```



## Configuration

Before running the script, you must update the academic calendar dates in `calendar_ics.py` to match the current quarter/semester:

1. Open `calendar_ics.py`.
2. Update the `QUARTER_START` and `QUARTER_END` variables (format: `YYYYMMDD`).
3. Update the `HOLIDAYS` set with the specific dates where classes should be cancelled.
4. (Optional) Change `TZID` if you are in a different time zone (default is `America/Los_Angeles`).

## Usage

Place your schedule PDF in the project directory and run the following command:

```bash
python calendar_ics.py <your_schedule_filename>.pdf

```

### Output

The script will generate a file named `schedule.ics` in the root directory. You can then import this file into your preferred calendar app.

## Requirements

* Python 3.10+ (utilizes `match` statements)
* `pymupdf`
* `pandas`

## Notes

* **PDF Layout**: The extraction logic in `extract_table.py` uses a specific crop box (`45, 50, 612 - 45, 792 - 50`). If your PDF has different margins, you may need to adjust these coordinates.
* **Course Codes**: The script assumes the course code is in the first column of the extracted table.