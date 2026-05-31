# webreg-to-ics

Convert a UCSD WebReg course schedule PDF into a calendar (.ics) file and preview your weekly schedule in the browser.

## Overview

Upload your WebReg schedule PDF to the web interface. The backend extracts the course table, builds recurring events with UC San Diego holidays excluded, and returns a standards-compliant `.ics` file ready to import into Google Calendar, Apple Calendar, Outlook, etc.

## Features

- Parses course schedule PDFs exported from UCSD WebReg
- Supports lectures, labs, discussions, finals, and midterms
- Handles recurring weekly events with holidays excluded
- Returns a standards-compliant `.ics` file
- Weekly calendar preview in the browser

## Project Structure

```
webreg-to-ics/
├── api/
│   └── index.py          # Vercel serverless entry point
├── public/
│   ├── index.html        # Frontend UI
│   ├── script.js
│   └── style.css
├── scripts/
│   ├── __init__.py
│   ├── calendar_ics.py   # Builds .ics from parsed data
│   ├── extract_table.py  # PDF table extraction (PyMuPDF)
│   ├── main_from_pdf.py  # Orchestrates extract → build
│   └── util.py           # Date/time helpers
├── server.py             # Local dev server (FastAPI + static files)
├── vercel.json           # Vercel rewrite rules
└── requirements.txt
```

## Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt`
- Modern web browser

## Usage

### Option 1 — Local dev server

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the server:
   ```bash
   uvicorn server:app --reload
   ```

3. Open [http://localhost:8000](http://localhost:8000) in your browser.

4. Download your schedule from WebReg (print as PDF), upload it, and download the generated `schedule.ics`.

### Option 2 — Deploy to Vercel

1. Install the [Vercel CLI](https://vercel.com/docs/cli) and log in.

2. Deploy:
   ```bash
   vercel
   ```

   The `vercel.json` rewrite routes `/convert` to the `api/index.py` serverless function. Host the `public/` directory as the frontend.

### Option 3 — Script only (no server)

Run the conversion directly from the command line:

```bash
pip install -r requirements.txt
python -c "from scripts.main_from_pdf import main_from_pdf; main_from_pdf('webregMain.pdf', 'schedule.ics')"
```

The output `schedule.ics` can be imported directly into any calendar app.

## Notes

- Holidays are automatically excluded from recurring events.
- The PDF must be the print/save-as-PDF output from UCSD WebReg.

## License

MIT License
