# WebReg to ICS

Convert a UCSD WebReg schedule PDF into a clean, importable calendar (`.ics`) file.

## Why This Exists

UCSD WebReg doesn't provide native calendar export. This tool bridges that gap by automatically extracting course data from your PDF and generating a standards-compliant `.ics` file compatible with Google Calendar, Apple Calendar, and Outlook.

## Features

- **PDF to Calendar**: Extracts course information via OCR
- **Weekly Lectures**: Automatically generates recurring lecture events
- **Holiday-Aware**: Skips UCSD holidays (MLK Day, Presidents' Day, etc.)
- **Exams Included**: Adds midterms and finals as one-off events
- **Clean Output**: Professional event titles like `MATH 171A Lecture`
- **Universal Compatibility**: Works with Google Calendar, Apple Calendar, and Outlook

## Installation

### System Dependencies

Install these first:
```bash
# macOS (Homebrew)
brew install tesseract poppler

# Ubuntu/Debian
sudo apt-get install tesseract-ocr poppler-utils

# Windows
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# https://blog.alivate.com.au/poppler-windows/
```

### Python Dependencies
```bash
pip install -r requirements.txt
```

Requires Python 3.9+

## Usage

1. Download your schedule from UCSD WebReg as a PDF
2. Run the tool:
```bash
python main.py
```

3. Enter your PDF filename when prompted
4. Import the generated `schedule.ics` into your calendar app

## Project Structure
```
webreg-to-ics/
├── main.py
├── requirements.txt
├── README.md
└── webreg_to_ics/
    ├── pdf_to_image.py    # PDF → image conversion
    ├── ocr.py             # OCR text extraction
    ├── parser.py          # Text → course data parsing
    └── calendar.py        # Data → .ics generation
```

## Limitations

- OCR accuracy depends on PDF quality
- Currently tuned for UCSD Winter 2026 schedules
- Parser updates may be needed if WebReg format changes

## License

MIT License