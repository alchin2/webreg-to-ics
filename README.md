## WebReg PDF → Calendar (.ics)

Convert a UC WebReg schedule PDF into a downloadable `.ics` calendar file with a live weekly preview.

**Features:** PDF → CSV extraction | Weekly calendar preview (FullCalendar) | Correct weekly recurrence | Stops before finals | One-click `.ics` download | Vercel-ready

---

## Quick Start

```bash
git clone <your-repo-url>
cd webreg_to_ics
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m api.index
```

Open `http://127.0.0.1:5000`

**CLI only?** Run `python main.py` for a quick `.ics` file without the web UI.

---

## How It Works

1. Upload your WebReg PDF
2. `pdf_extract.py` detects the course table and exports CSV
3. `calendar.py` converts CSV → standards-compliant `.ics`
4. Preview shows weekly recurring events (classes stop before finals)
5. Download and import into Google Calendar, Outlook, Apple Calendar, etc.

---

## Project Structure

```
webreg_to_ics/
├── api/index.py              # Flask backend
├── webreg/calendar.py        # CSV → ICS logic
├── webreg/pdf_extract.py     # PDF table extraction
├── templates/index.html      # Frontend + calendar preview
├── main.py                   # CLI script
├── requirements.txt
├── vercel.json
└── README.md
```

---

## Deployment (Vercel)

```json
{
  "builds": [{ "src": "api/index.py", "use": "@vercel/python" }],
  "routes": [{ "src": "/.*", "dest": "api/index.py" }]
}
```

Import repo to Vercel and deploy.

---

## Notes

- PDF must follow standard WebReg format
- Preview is visualization only; `.ics` file is the source of truth

---

## License

### MIT License

