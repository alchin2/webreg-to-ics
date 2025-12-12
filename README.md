# WebReg to ICS

Convert a UCSD WebReg schedule PDF into a calendar (`.ics`) file using OCR.

This tool takes your WebReg PDF, extracts course information, and generates a
calendar that includes:
- Weekly lectures
- Skipped holidays
- One-off midterms and finals

The output `.ics` file can be imported into Google Calendar, Apple Calendar,
Outlook, and other calendar apps.

---

## Features

- PDF → Image → OCR → Structured data → `.ics`
- Handles common OCR errors automatically
- Weekly recurring classes (no finals week)
- Skips UCSD holidays (MLK Day, Presidents’ Day)
- Adds midterms and finals as single events
- Clean, minimal calendar event titles

---

## Requirements

You must have the following installed on your system:

- **Python 3.9+**
- **Tesseract OCR**
- **Poppler** (for `pdf2image`)

On macOS (Homebrew):

```bash
brew install tesseract poppler
